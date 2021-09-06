#!/usr/bin/env python

import time
import pandas as pd

from transform.utils import sha1sum, write_timestamp_file


def computeStats(update_time):
    filename = 'csv/stats.csv'
    print("Processing", filename)
    old_hash = sha1sum(filename)

    df_patients = pd.read_csv('csv/patients.csv', index_col='date', parse_dates=['date'])[[
        'state.in_hospital', 'state.in_hospital.todate', 'state.icu', 'state.critical', 'state.out_of_hospital.todate',
        'state.deceased.todate'
    ]]

    df_phases = pd.read_csv('csv/dict-phases.csv', index_col='date.from', parse_dates=['date.from']).rename(mapper={'id': 'phase'}, axis='columns')[['phase']]
    df_phases = df_phases.reindex(pd.date_range(df_phases.index.min(), df_patients.index.max(), freq='D'), method='ffill')
    df_phases.index.name = 'date'

    dfRegions = pd.read_csv('csv/region-confirmed.csv', index_col='date', parse_dates=['date'])
    dfAgeC = pd.read_csv('csv/age-cases.csv', index_col='date', parse_dates=['date'])
    dfAgeD = pd.read_csv('csv/age-deceased.csv', index_col='date', parse_dates=['date'])
    dfRhD = pd.read_csv('csv/rh-deceased.csv', index_col='date', parse_dates=['date'])
    dfVaccination = pd.read_csv('csv/vaccination.csv', index_col='date', parse_dates=['date'])
    df_lab_tests = pd.read_csv('csv/lab-tests.csv', index_col='date', parse_dates=['date'])[[
        'tests.performed', 'tests.performed.todate', 'tests.positive', 'tests.positive.todate', 'tests.regular.performed',
        'tests.regular.performed.todate', 'tests.regular.positive', 'tests.regular.positive.todate',
        'tests.hagt.performed', 'tests.hagt.performed.todate', 'tests.hagt.positive', 'tests.hagt.positive.todate',
        'tests.ns-apr20.performed', 'tests.ns-apr20.performed.todate', 'tests.ns-apr20.positive', 'tests.ns-apr20.positive.todate',
    ]]
    df_cases = pd.read_csv('csv/cases.csv', index_col='date', parse_dates=['date'])[[
        'cases.confirmed', 'cases.confirmed.todate', 'cases.active', 'cases.recovered.todate', 'cases.closed.todate',
        'cases.hs.employee.confirmed.todate', 'cases.rh.employee.confirmed.todate', 'cases.rh.occupant.confirmed.todate',
        'cases.vaccinated.confirmed.todate'
    ]]
    merged = df_phases.join(df_patients).join(dfRegions).join(dfAgeC).join(dfAgeD).join(dfRhD).join(df_lab_tests).join(df_cases).join(dfVaccination)
    merged['cases.unclassified.confirmed.todate'] = merged['cases.confirmed.todate'] \
        .sub(merged['cases.hs.employee.confirmed.todate'], fill_value=0) \
        .sub(merged['cases.rh.employee.confirmed.todate'], fill_value=0) \
        .sub(merged['cases.rh.occupant.confirmed.todate'], fill_value=0)

    merged.insert(loc=0, column='day', value=range(-8, -8 + len(merged)))
    merged.reset_index(inplace=True)
    merged.set_index('day', inplace=True)

    merged = merged.reindex([  # sort
        'date', 'phase', 'tests.performed.todate', 'tests.performed', 'tests.positive.todate', 'tests.positive', 'tests.regular.performed.todate',
        'tests.regular.performed', 'tests.regular.positive.todate', 'tests.regular.positive',
        'tests.hagt.performed', 'tests.hagt.performed.todate', 'tests.hagt.positive', 'tests.hagt.positive.todate',
        'tests.ns-apr20.performed.todate', 'tests.ns-apr20.performed',
        'tests.ns-apr20.positive.todate', 'tests.ns-apr20.positive',
        'cases.confirmed.todate', 'cases.confirmed', 'cases.active', 'cases.recovered.todate',
        'cases.closed.todate', 'cases.hs.employee.confirmed.todate', 'cases.rh.employee.confirmed.todate', 'cases.rh.occupant.confirmed.todate',
        'cases.unclassified.confirmed.todate', 'cases.vaccinated.confirmed.todate', 'state.in_hospital', 'state.icu', 'state.critical', 'state.in_hospital.todate', 'state.out_of_hospital.todate',
        'state.deceased.todate', 'region.lj.todate', 'region.ce.todate', 'region.mb.todate', 'region.ms.todate', 'region.kr.todate',
        'region.nm.todate', 'region.za.todate', 'region.sg.todate', 'region.po.todate', 'region.ng.todate', 'region.kp.todate', 'region.kk.todate',
        'region.foreign.todate', 'region.unknown.todate', 'region.todate', 'age.0-4.todate', 'age.5-14.todate', 'age.15-24.todate', 'age.25-34.todate',
        'age.35-44.todate', 'age.45-54.todate', 'age.55-64.todate', 'age.65-74.todate', 'age.75-84.todate', 'age.85+.todate', 'age.todate',
        'age.female.0-4.todate', 'age.female.5-14.todate', 'age.female.15-24.todate', 'age.female.25-34.todate', 'age.female.35-44.todate',
        'age.female.45-54.todate', 'age.female.55-64.todate', 'age.female.65-74.todate', 'age.female.75-84.todate', 'age.female.85+.todate',
        'age.female.todate', 'age.male.0-4.todate', 'age.male.5-14.todate', 'age.male.15-24.todate', 'age.male.25-34.todate', 'age.male.35-44.todate',
        'age.male.45-54.todate', 'age.male.55-64.todate', 'age.male.65-74.todate', 'age.male.75-84.todate', 'age.male.85+.todate', 'age.male.todate',

        'age.unknown.0-4.todate', 'age.unknown.5-14.todate', 'age.unknown.15-24.todate', 'age.unknown.25-34.todate', 'age.unknown.35-44.todate',
        'age.unknown.45-54.todate', 'age.unknown.55-64.todate', 'age.unknown.65-74.todate', 'age.unknown.75-84.todate', 'age.unknown.85+.todate',
        'age.unknown.todate',

        'deceased.0-4.todate', 'deceased.5-14.todate', 'deceased.15-24.todate', 'deceased.25-34.todate', 'deceased.35-44.todate', 'deceased.45-54.todate',
        'deceased.55-64.todate', 'deceased.65-74.todate', 'deceased.75-84.todate', 'deceased.85+.todate', 'deceased.todate', 'deceased.female.0-4.todate',
        'deceased.female.5-14.todate', 'deceased.female.15-24.todate', 'deceased.female.25-34.todate', 'deceased.female.35-44.todate', 'deceased.female.45-54.todate',
        'deceased.female.55-64.todate', 'deceased.female.65-74.todate', 'deceased.female.75-84.todate', 'deceased.female.85+.todate', 'deceased.female.todate',
        'deceased.male.0-4.todate', 'deceased.male.5-14.todate', 'deceased.male.15-24.todate', 'deceased.male.25-34.todate', 'deceased.male.35-44.todate',
        'deceased.male.45-54.todate', 'deceased.male.55-64.todate', 'deceased.male.65-74.todate', 'deceased.male.75-84.todate', 'deceased.male.85+.todate',
        'deceased.male.todate', 'deceased.rhoccupant.todate', 'deceased.other.todate',
        'vaccination.administered', 'vaccination.administered.todate',
        'vaccination.administered2nd', 'vaccination.administered2nd.todate',
        'vaccination.used.todate', 'vaccination.delivered.todate'
    ], axis='columns')

    merged.to_csv(filename, float_format='%.0f', line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=old_hash)

def computeMunicipalityCases(update_time):
    filename = 'csv/municipality-cases.csv'
    print("Processing", filename)
    old_hash = sha1sum(filename)
    dfConfirmed = pd.read_csv('csv/municipality-confirmed.csv', index_col='date')
    dfActive = pd.read_csv('csv/municipality-active.csv', index_col='date')
    dfDeceased = pd.read_csv('csv/municipality-deceased.csv', index_col='date')
    dfVaccinated = pd.read_csv('csv/vaccination-by_municipality.csv', index_col='date')
    dfConfirmed.columns = [str(col) + '.cases.confirmed.todate' for col in dfConfirmed.columns]
    dfActive.columns = [str(col) + '.cases.active' for col in dfActive.columns]
    dfDeceased.columns = [str(col) + '.deceased.todate' for col in dfDeceased.columns]
    dfVaccinated = dfVaccinated.filter(like='date', axis='columns') \
                    .rename(mapper=lambda x: x.replace('vaccination.region', 'region'), axis='columns') \
                    .rename(mapper=lambda x: x.replace('1st.todate', 'vaccinated.1st.todate'), axis='columns') \
                    .rename(mapper=lambda x: x.replace('2nd.todate', 'vaccinated.2nd.todate'), axis='columns')
    merged = dfConfirmed.join(dfActive).join(dfDeceased).join(dfVaccinated).sort_index(axis=1)
    merged.to_csv(filename, float_format='%.0f', index_label='date')
    write_timestamp_file(filename=filename, old_hash=old_hash)

def computeRegionCases(update_time):
    filename = 'csv/region-cases.csv'
    print("Processing", filename)
    old_hash = sha1sum(filename)
    dfConfirmed = pd.read_csv('csv/region-confirmed.csv', index_col='date')
    dfActive = pd.read_csv('csv/region-active.csv', index_col='date')
    dfDeceased = pd.read_csv('csv/region-deceased.csv', index_col='date')
    dfVaccinated = pd.read_csv('csv/vaccination-by_region.csv', index_col='date')
    dfConfirmed = dfConfirmed.rename(mapper=lambda x: x.replace('todate', 'cases.confirmed.todate'), axis='columns') \
                    .drop('region.cases.confirmed.todate', axis='columns') 
    dfActive = dfActive.rename(mapper=lambda x: x.replace('active', 'cases.active'), axis='columns') \
                    .drop('region.cases.active', axis='columns') 
    dfDeceased = dfDeceased.rename(mapper=lambda x: x.replace('todate', 'deceased.todate'), axis='columns') \
                    .drop('region.deceased.todate', axis='columns') 
    dfVaccinated = dfVaccinated.filter(like='date', axis='columns') \
                    .rename(mapper=lambda x: x.replace('vaccination.region', 'region'), axis='columns') \
                    .rename(mapper=lambda x: x.replace('1st.todate', 'vaccinated.1st.todate'), axis='columns') \
                    .rename(mapper=lambda x: x.replace('2nd.todate', 'vaccinated.2nd.todate'), axis='columns')
    merged = dfConfirmed.join(dfActive).join(dfDeceased).join(dfVaccinated).sort_index(axis=1)
    merged.to_csv(filename, float_format='%.0f', index_label='date')
    write_timestamp_file(filename=filename, old_hash=old_hash)


def computeCases(update_time):
    filename = 'csv/cases.csv'
    print("Processing", filename)

    # LAB (9:00): cases.confirmed, cases.confirmed.todate, cases.active, cases.closed
    df_cases = pd.read_csv(filename, index_col='date')
    df_cases_old_hash = sha1sum(filename)
    df_lab_tests = pd.read_csv('csv/lab-tests.csv', index_col='date').replace({None: 0})
    date_diff = df_lab_tests.index.difference(df_cases.index)
    date_diff = [date for date in date_diff if date not in {  # discard irrelevant early days
        '2020-02-02', '2020-02-09', '2020-02-16', '2020-02-23', '2020-02-24', '2020-02-25', '2020-02-26',
        '2020-02-27', '2020-02-28', '2020-02-29', '2020-03-01', '2020-03-02', '2020-03-03'
    }]
    assert len(date_diff) <= 1, 'The date difference between lab-tests.csv and cases.csv is more than one day.'
    if len(date_diff) > 0:
        df_cases = df_cases.append(pd.DataFrame(index=date_diff, columns=df_cases.columns))
        date = date_diff[0]  # equals index of -1
        # only manipulate last row
        df_cases.at[date, 'cases.confirmed'] = df_lab_tests.at[date, 'tests.positive'] + df_lab_tests.at[date, 'tests.hagt.positive']
        df_cases.at[date, 'cases.confirmed.todate'] = df_cases.iloc[-2, df_cases.columns.get_loc('cases.confirmed.todate')] + df_cases.at[date, 'cases.confirmed']

        df_cases['cases.active.temp'] = df_cases['cases.confirmed'].rolling(window=14).sum()
        df_cases.at[date, 'cases.active'] = df_cases.at[date, 'cases.active.temp']
        df_cases.drop('cases.active.temp', axis='columns', inplace=True)

        df_cases.at[date, 'cases.closed.todate'] = df_cases.at[date, 'cases.confirmed.todate'] - df_cases.at[date, 'cases.active']

        # TODO use common function for writing CSV
        df_cases.index.rename('date', inplace=True)  # name it explicitly otherwise it doesn't show up in csv
        df_cases.replace({0: None}).astype('Int64').to_csv(filename, line_terminator='\r\n')
        write_timestamp_file(filename=filename, old_hash=df_cases_old_hash)

    # HOS (10:30): cases.recovered.todate
    df_patients = pd.read_csv('csv/patients.csv', index_col='date')
    df_cases['cases.recovered.todate'] = df_cases['cases.closed.todate'] - df_patients['state.deceased.todate'].shift(-1)
    df_cases = df_cases.reindex([
        'cases.confirmed', 'cases.confirmed.todate', 'cases.active', 'cases.closed.todate', 'cases.recovered.todate',
        'cases.rh.occupant.confirmed.todate', 'cases.hs.employee.confirmed.todate', 'cases.rh.employee.confirmed.todate',
        'cases.vaccinated.confirmed.todate'
    ], axis='columns')

    df_cases.replace({0: None}).astype('Int64').to_csv(filename, line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=df_cases_old_hash)

if __name__ == "__main__":
    update_time = int(time.time())

    computeMunicipalityCases(update_time)
    computeRegionCases(update_time)
    computeCases(update_time)
    computeStats(update_time)

