import datetime
import pathlib
import os
import os.path
import time
import pandas as pd
import sheet2csv

from transform.utils import sha1sum, write_timestamp_file
from update_stats import computeStats


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

if __name__ == "__main__":
    update_time = int(time.time())
    import_sheet(update_time, SHEET_MEAS, RANGE_SAFETY_MEASURES, "csv/safety_measures.csv")
    import_sheet(update_time, SHEET_TESTS, RANGE_LAB_TESTS, "csv/lab-tests.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_PATIENTS, "csv/patients.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_HOSPITALS, "csv/hospitals.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_ICU, "csv/icu.csv")

    computeMunicipalityCases(update_time)
    computeRegionCases(update_time)
    computeCases(update_time)
    computeStats(update_time)

