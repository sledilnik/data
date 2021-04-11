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

    dfRegions = pd.read_csv('csv/region-confirmed.csv', index_col='date')
    dfAgeC = pd.read_csv('csv/age-cases.csv', index_col='date')
    dfAgeD = pd.read_csv('csv/age-deceased.csv', index_col='date')
    dfRhD = pd.read_csv('csv/rh-deceased.csv', index_col='date')
    dfVaccination = pd.read_csv('csv/vaccination.csv', index_col='date')
    df_lab_tests = pd.read_csv('csv/lab-tests.csv', index_col='date')[[
        'tests.performed', 'tests.performed.todate', 'tests.positive', 'tests.positive.todate', 'tests.regular.performed',
        'tests.regular.performed.todate', 'tests.regular.positive', 'tests.regular.positive.todate',
        'tests.hagt.performed', 'tests.hagt.performed.todate', 'tests.hagt.positive', 'tests.hagt.positive.todate',
        'tests.ns-apr20.performed', 'tests.ns-apr20.performed.todate', 'tests.ns-apr20.positive', 'tests.ns-apr20.positive.todate',
    ]]
    df_cases = pd.read_csv('csv/cases.csv', index_col='date')[[
        'cases.confirmed', 'cases.confirmed.todate', 'cases.active', 'cases.recovered.todate', 'cases.closed.todate',
        'cases.hs.employee.confirmed.todate', 'cases.rh.employee.confirmed.todate', 'cases.rh.occupant.confirmed.todate',
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
        'cases.unclassified.confirmed.todate', 'state.in_hospital', 'state.icu', 'state.critical', 'state.in_hospital.todate', 'state.out_of_hospital.todate',
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


if __name__ == "__main__":
    update_time = int(time.time())
    computeStats(update_time)

