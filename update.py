import datetime
import pathlib
import os
import os.path
import time
import pandas as pd
import cepimose
import sheet2csv

from transform.utils import sha1sum, write_timestamp_file


SHEET_ID_DEV = "1GDYUsjtJMub8Gh_hZMu4UQw6hAVmtUh6E0rS9dlUl3o"

SHEET_MAIN = "1N1qLMoWyi3WFGhIpPFzKsFmVE0IwNP3elb_c18t2DwY"

RANGE_STATS = "Podatki!A3:ZZ"
RANGE_STATS_LEGACY = "Podatki!A3:AK"
RANGE_REGIONS = "Kraji!A1:ZZ"
RANGE_DSO = "DSO!A3:ZZ"
RANGE_SCHOOLS = "Šole!A3:ZZ"
RANGE_DECEASED_REGIONS = "Umrli:Kraji!A1:ZZ"
RANGE_ACTIVE_REGIONS = "Aktivni:Kraji!A1:ZZ"
RANGE_STATS_WEEKLY = "EPI:weekly!A3:ZZ"

SHEET_HOS = "1jCrsfiJwb_6N39WebN280D3axVvU0Vblk2XpfPI0zMk"
RANGE_PATIENTS_SUMMARY = "E:PatientsSummary!A1:ZZ"
RANGE_PATIENTS = "E:Patients!A3:ZZ"
RANGE_HOSPITALS = "E:Hospitals!A3:ZZ"
RANGE_ICU = "E:ICU!A4:ZZ"

SHEET_VACC = "1uGsMr0w2acVw4VkoOTEWVtBSwChsnFzKRLnRaYQFXVE"
RANGE_VACC_DELIVERED = "E:Delivered!A3:ZZ"

SHEET_TESTS = "1Mo6D2UlMvGE_-ZtF7aihnqVuUxTIdGGE-tIBBUxj0T0"
RANGE_LAB_TESTS = "E:LAB-Tests!A3:ZZ"

SHEET_MEAS = "1AzBziQ5ySEaY8cv4NMYfc1LopTWbBRX0hWzMVP8Q52M"
RANGE_SAFETY_MEASURES = "E:Measures!A3:ZZ"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


def import_sheet(update_time, sheet, range, filename, **kwargs):
    print("Processing", filename)
    pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    old_hash = sha1sum(filename)
    try:
        sheet2csv.sheet2csv(id=sheet, range=range, api_key=GOOGLE_API_KEY, filename=filename, **kwargs)
    except Exception as e:
        print("Failed to import {}".format(filename))
        raise e
    write_timestamp_file(filename=filename, old_hash=old_hash)


def computeMunicipalityCases(update_time):
    filename = 'csv/municipality-cases.csv'
    print("Processing", filename)
    old_hash = sha1sum(filename)
    dfConfirmed = pd.read_csv('csv/municipality-confirmed.csv', index_col='date')
    dfActive = pd.read_csv('csv/municipality-active.csv', index_col='date')
    dfDeceased = pd.read_csv('csv/municipality-deceased.csv', index_col='date')
    dfConfirmed.columns = [str(col) + '.cases.confirmed.todate' for col in dfConfirmed.columns]
    dfActive.columns = [str(col) + '.cases.active' for col in dfActive.columns]
    dfDeceased.columns = [str(col) + '.deceased.todate' for col in dfDeceased.columns]
    merged = dfConfirmed.join(dfActive).join(dfDeceased).sort_index(axis=1)
    merged.to_csv(filename, float_format='%.0f', index_label='date')
    write_timestamp_file(filename=filename, old_hash=old_hash)

def computeRegionCases(update_time):
    filename = 'csv/region-cases.csv'
    print("Processing", filename)
    old_hash = sha1sum(filename)
    dfConfirmed = pd.read_csv('csv/region-confirmed.csv', index_col='date')
    dfActive = pd.read_csv('csv/region-active.csv', index_col='date')
    dfDeceased = pd.read_csv('csv/region-deceased.csv', index_col='date')
    dfConfirmed = dfConfirmed.rename(mapper=lambda x: x.replace('todate', 'cases.confirmed.todate'), axis='columns') \
                    .drop('region.cases.confirmed.todate', axis='columns') 
    dfActive = dfActive.rename(mapper=lambda x: x.replace('active', 'cases.active'), axis='columns') \
                    .drop('region.cases.active', axis='columns') 
    dfDeceased = dfDeceased.rename(mapper=lambda x: x.replace('todate', 'deceased.todate'), axis='columns') \
                    .drop('region.deceased.todate', axis='columns') 
    merged = dfConfirmed.join(dfActive).join(dfDeceased).sort_index(axis=1)
    merged.to_csv(filename, float_format='%.0f', index_label='date')
    write_timestamp_file(filename=filename, old_hash=old_hash)

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
        'cases.rh.occupant.confirmed.todate', 'cases.hs.employee.confirmed.todate', 'cases.rh.employee.confirmed.todate'
    ], axis='columns')

    df_cases.replace({0: None}).astype('Int64').to_csv(filename, line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=df_cases_old_hash)


def computeVaccination(update_time):
    filename = 'csv/vaccination.csv'
    print("Processing", filename)
    old_hash = sha1sum(filename)

    df_a= pd.read_csv('csv/vaccination-administered.csv', index_col='date')

    df_d= pd.read_csv('csv/vaccination-delivered.csv', index_col='date')

    merged = df_a.join(df_d, how='outer')
    merged['vaccination.pfizer.delivered.todate'] = \
        merged['vaccination.pfizer.delivered'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    merged['vaccination.moderna.delivered.todate'] = \
        merged['vaccination.moderna.delivered'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    merged['vaccination.az.delivered.todate'] = \
        merged['vaccination.az.delivered'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    merged['vaccination.delivered.todate'] = merged['vaccination.pfizer.delivered.todate'] \
        .add(merged['vaccination.moderna.delivered.todate'], fill_value=0) \
        .add(merged['vaccination.az.delivered.todate'], fill_value=0).astype('Int64')

    merged = merged.reindex([  # sort
        'vaccination.administered', 'vaccination.administered.todate',
        'vaccination.administered2nd', 'vaccination.administered2nd.todate',
        'vaccination.used.todate', 
        'vaccination.delivered.todate',
        'vaccination.pfizer.delivered', 'vaccination.pfizer.delivered.todate', 
        'vaccination.moderna.delivered', 'vaccination.moderna.delivered.todate', 
        'vaccination.az.delivered', 'vaccination.az.delivered.todate'
    ], axis='columns')
    merged.to_csv(filename, float_format='%.0f', line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=old_hash)


def import_nijz_dash_vacc_administred():
    filename = "csv/vaccination-administered.csv"
    
    df = pd.DataFrame.from_dict(cepimose.vaccinations_by_day()).set_index('date').rename(columns={
        'first_dose': 'vaccination.administered.todate',
        'second_dose': 'vaccination.administered2nd.todate'
    })

    # dummy row for diff calculation remowed afterwards
    dummy_date = datetime.datetime(2020, 12, 26)
    dummy_row = pd.DataFrame({
        'vaccination.administered.todate': 0,
        'vaccination.administered2nd.todate': 0
    }, index=[dummy_date])

    # calculate diffs from cumulative values (vaccinations per day)
    df_diff = pd.concat([dummy_row, df]).diff().drop(labels=[dummy_date]).rename(columns={
        'vaccination.administered.todate': 'vaccination.administered',
        'vaccination.administered2nd.todate': 'vaccination.administered2nd'
    }).astype('Int64')

    # merge dataframes (cumulative and per day)
    df = pd.merge(df, df_diff, right_index=True, left_index=True)

    # calcualte used vaccine doeses
    df['vaccination.used.todate'] = df['vaccination.administered.todate'] + 2*df['vaccination.administered2nd.todate']
    # sort cols
    df = df[['vaccination.administered', 'vaccination.administered.todate', 'vaccination.administered2nd', 'vaccination.administered2nd.todate', 'vaccination.used.todate']]
    
    # write csv
    old_hash = sha1sum(filename)
    # replace 0 with pd.NA so it does not get written to CSV
    df.replace(0, pd.NA).to_csv(filename, date_format='%Y-%m-%d')
    write_timestamp_file(filename, old_hash)

def import_nijz_dash_vacc_delivered():
    filename = "csv/vaccination-delivered.csv"
    
    df = pd.DataFrame.from_dict(cepimose.vaccines_supplied_by_manufacturer()).rename(columns={
        'pfizer': 'vaccination.pfizer.delivered',
        'moderna': 'vaccination.moderna.delivered',
        'az': 'vaccination.az.delivered',
    }).set_index('date')

    # sort columns
    df = df[['vaccination.pfizer.delivered','vaccination.moderna.delivered','vaccination.az.delivered']]
    
    # write csv
    old_hash = sha1sum(filename)
    # force integer type
    df.astype('Int64').to_csv(filename, date_format="%Y-%m-%d", line_terminator='\r\n')
    write_timestamp_file(filename, old_hash)

def import_nijz_dash_vacc_by_age():
    filename = "csv/vaccination-by_age.csv"
    df_existing = pd.read_csv(filename, index_col=0, parse_dates=[0])
    
    today_data = {}
    for row in cepimose.vaccinations_by_age():
        today_data["vaccination.age.{}.1st.todate".format(row.age_group)] = row.count_first
        today_data["vaccination.age.{}.2nd.todate".format(row.age_group)] = row.count_second

    df_today = pd.DataFrame([today_data], index=[datetime.date.today()])
    df_today.index.name = 'date'
    
    def start_age(colname: str):
        return int(colname.split('.')[2].split('-')[0].strip('+'))

    def phase(colname: str):
        return colname.split('.')[3]

    # columns to be calculates
    columns_1864_1st = list(filter(lambda s: start_age(s) < 65 and phase(s) == '1st', df_today.columns))
    columns_1864_2nd = list(filter(lambda s: start_age(s) < 65 and phase(s) == '2nd', df_today.columns))
    columns_65_1st = list(filter(lambda s: start_age(s) >= 65 and phase(s) == '1st', df_today.columns))
    columns_65_2nd = list(filter(lambda s: start_age(s) >= 65 and phase(s) == '2nd', df_today.columns))
    df_today['vaccination.age.18-64.1st.todate'] = df_today[columns_1864_1st].sum(axis=1)
    df_today['vaccination.age.18-64.2nd.todate'] = df_today[columns_1864_2nd].sum(axis=1)
    df_today['vaccination.age.65+.1st.todate'] = df_today[columns_65_1st].sum(axis=1)
    df_today['vaccination.age.65+.2nd.todate'] = df_today[columns_65_2nd].sum(axis=1)

    df_updated = df_today.combine_first(df_existing).astype('Int64')

    col_order = ['vaccination.age.0-17.1st.todate',
        'vaccination.age.0-17.2nd.todate',
        'vaccination.age.18-24.1st.todate',
        'vaccination.age.18-24.2nd.todate',
        'vaccination.age.25-29.1st.todate',
        'vaccination.age.25-29.2nd.todate',
        'vaccination.age.30-34.1st.todate',
        'vaccination.age.30-34.2nd.todate',
        'vaccination.age.35-39.1st.todate',
        'vaccination.age.35-39.2nd.todate',
        'vaccination.age.40-44.1st.todate',
        'vaccination.age.40-44.2nd.todate',
        'vaccination.age.45-49.1st.todate',
        'vaccination.age.45-49.2nd.todate',
        'vaccination.age.50-54.1st.todate',
        'vaccination.age.50-54.2nd.todate',
        'vaccination.age.55-59.1st.todate',
        'vaccination.age.55-59.2nd.todate',
        'vaccination.age.60-64.1st.todate',
        'vaccination.age.60-64.2nd.todate',
        'vaccination.age.65-69.1st.todate',
        'vaccination.age.65-69.2nd.todate',
        'vaccination.age.70-74.1st.todate',
        'vaccination.age.70-74.2nd.todate',
        'vaccination.age.75-79.1st.todate',
        'vaccination.age.75-79.2nd.todate',
        'vaccination.age.80-84.1st.todate',
        'vaccination.age.80-84.2nd.todate',
        'vaccination.age.85-89.1st.todate',
        'vaccination.age.85-89.2nd.todate',
        'vaccination.age.90+.1st.todate',
        'vaccination.age.90+.2nd.todate',
        'vaccination.age.18-64.1st.todate',
        'vaccination.age.18-64.2nd.todate',
        'vaccination.age.65+.1st.todate',
        'vaccination.age.65+.2nd.todate']
    
    df_updated = df_updated[col_order]

    old_hash = sha1sum(filename)
    df_updated.astype('Int64').to_csv(filename, date_format='%Y-%m-%d')
    write_timestamp_file(filename, old_hash)


if __name__ == "__main__":
    update_time = int(time.time())
    import_sheet(update_time, SHEET_MEAS, RANGE_SAFETY_MEASURES, "csv/safety_measures.csv")
    import_sheet(update_time, SHEET_VACC, RANGE_VACC_DELIVERED, "csv/vaccination-delivered.csv")
    import_sheet(update_time, SHEET_TESTS, RANGE_LAB_TESTS, "csv/lab-tests.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_PATIENTS, "csv/patients.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_HOSPITALS, "csv/hospitals.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_ICU, "csv/icu.csv")

    import_nijz_dash_vacc_administred()
    import_nijz_dash_vacc_delivered()
    import_nijz_dash_vacc_by_age()

    computeMunicipalityCases(update_time)
    computeRegionCases(update_time)
    computeCases(update_time)
    computeVaccination(update_time)
    computeStats(update_time)

    