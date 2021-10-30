#!/usr/bin/env python
import time
import requests
import pandas as pd

from update_stats import sha1sum, write_timestamp_file, computeCases, computeStats

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


if __name__ == "__main__":
    update_time = int(time.time())

    import_opsi_vaccination_effects()

    computeVaccinatedCases(update_time)
    computeCases(update_time)
    computeStats(update_time)
