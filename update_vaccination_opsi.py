#!/usr/bin/env python
import time
from datetime import date 
import requests
import pandas as pd

from update_stats import sha1sum, write_timestamp_file, computeCases, computeStats
from transform.country_codes import stats_weekly_sorted_fields

def saveurl(url, filename, expectedContentType):
    print("Downloading ", url)
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()

    actualContentType = r.headers['Content-Type']

    if actualContentType == expectedContentType:
        open(filename, 'wb').write(r.content)
        print("Saved", filename)
    else:
        raise Exception("Unexpected content-type:", actualContentType)

def import_opsi_vaccination_effects():
    # https://podatki.gov.si/dataset/potrjeni-primeri-covid-19-po-cepljenju
    saveurl("https://podatki.gov.si/dataset/47edd697-a06b-44a6-86b7-0092ea34274a/resource/eb4bd862-737d-47f0-8e0a-47541986c2c3/download/pc14dnipozpublic.csv", "csv/vaccination-confirmed-cases-opsi.csv", "text/csv")

    # https://podatki.gov.si/dataset/hospitalizirani-primeri-sari-potrjeni-covid-19-po-cepilnem-statusu-v-sloveniji-nijz-cnb
    saveurl("https://podatki.gov.si/dataset/2a40d74b-4e75-4051-8ab7-289c70348cb7/resource/816af1be-4e56-4fca-a647-db7b09a2c98b/download/saricov19hospitalizacija.csv", "csv/vaccination-hospitalized-cases-opsi.csv", "text/csv")


def computeVaccinatedCases(update_time):
    filename = 'csv/cases-vaccinated.csv'
    print("Processing", filename)
    df_old_hash = sha1sum(filename)
    vaccination_column_name = 'Potrjeni zasciteni s cepljenjem'
    df_vaccination_cases = pd.read_csv('csv/vaccination-confirmed-cases-opsi.csv',
        sep=';',
        decimal=',',
        thousands='.',
        usecols=['Datum', vaccination_column_name],
        index_col='Datum',
        parse_dates=['Datum'],
        date_parser=lambda date_string: pd.to_datetime(date_string, format="%d.%m.%Y"),
        dtype={vaccination_column_name: 'int64'})
    df_vaccination_cases['cases.vaccinated.confirmed.todate'] = df_vaccination_cases[vaccination_column_name].cumsum().astype('Int64')
    df_vaccination_cases = df_vaccination_cases [[ 'cases.vaccinated.confirmed.todate' ]]
    df_vaccination_cases.index.names = ['date']

    df_vaccination_cases.replace({0: None}).astype('Int64').dropna().to_csv(filename, line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=df_old_hash)


def computeVaccinatedCasesWeekly(update_time):
    filename = 'csv/cases-vaccinated-weekly.csv'
    print("Processing", filename)
    df_old_hash = sha1sum(filename)

    # source hospitalized+vaccinated data from OPSI CSV
    df_hospitalized_cases = pd.read_csv('csv/vaccination-hospitalized-cases-opsi.csv', sep=';') \
        .rename(mapper={
            'Leto': 'year',
            'Teden': 'week',
            'Hosp_Necepljeni': 'week.hospitalized.other',
            'Hosp_Cepljeni': 'week.hospitalized.vaccinated'
        }, axis='columns')

    df_hospitalized_cases['week'] = df_hospitalized_cases['year'].astype('str') + df_hospitalized_cases['week'].map(lambda x: '-%02d' % x)
    df_hospitalized_cases.set_index('week', inplace=True)
    df_hospitalized_cases = df_hospitalized_cases[[ 'week.hospitalized.vaccinated', 'week.hospitalized.other' ]].astype('Int64')

    # source icu hospitalized from ICU CSV
    vaccination_statuses = ['vaccinated', 'vaccinatedpartially', 'recovered', 'other']
    icu_columns_daily = ['date'] + list(map(lambda status: 'state.icu.in.' + status, vaccination_statuses))
    df_icu_cases = pd.read_csv('csv/icu.csv', usecols=icu_columns_daily)
    # convert to datetime objects
    df_icu_cases['date'] = pd.to_datetime(df_icu_cases['date'])
    # calculate weekly cumulative sum, convert to integers and rename columns
    df_icu_cases = df_icu_cases \
        .resample('W-Mon', on='date', closed='left', label='left').sum().replace({0: None}).astype('Int64') \
        .rename(columns = dict(map(lambda status: ('state.icu.in.' + status, 'week.icu.' + status), vaccination_statuses)))
    df_icu_cases['week'] = df_icu_cases.index.strftime('%Y-%W')
    df_icu_cases.set_index('week', inplace=True)
    df_icu_cases = df_icu_cases[df_icu_cases.index < date.today().strftime('%Y-%W')] # drop current week: incomplete

    merged = df_hospitalized_cases.join(df_icu_cases, how='outer')
    merged.index.name = 'week'

    merged.astype('Int64').dropna(thresh=1).to_csv(filename, line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=df_old_hash)


def computeStatsWeekly(update_time):
    filename = 'csv/stats-weekly.csv'
    print("Processing", filename)
    df_old_hash = sha1sum(filename)

    fields_vacc = [
        'week.hospitalized.vaccinated', 'week.hospitalized.other',
        'week.icu.vaccinated', 'week.icu.vaccinatedpartially', 'week.icu.recovered', 'week.icu.other'
    ]

    df_stats_weekly = pd.read_csv(filename, index_col='week')
    df_stats_weekly.drop(fields_vacc, axis='columns', inplace=True)

    df_vaccinated = pd.read_csv('csv/cases-vaccinated-weekly.csv', index_col='week')

    merged = df_stats_weekly.join(df_vaccinated).reindex(stats_weekly_sorted_fields, axis='columns')

    for field in stats_weekly_sorted_fields[2:]:
        merged[field] = merged[field].astype('Int64')

    merged.to_csv(filename, line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=df_old_hash)


if __name__ == "__main__":
    update_time = int(time.time())

    import_opsi_vaccination_effects()

    computeVaccinatedCases(update_time)
    computeVaccinatedCasesWeekly(update_time)
    computeCases(update_time)
    computeStats(update_time)
    computeStatsWeekly(update_time)
