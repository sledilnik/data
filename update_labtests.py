#!/usr/bin/env python

import time
from datetime import date, datetime, timedelta
import pandas as pd
import cepimose
from update_stats import computeStats, computeCasesWithCount

from transform.utils import sha1sum, write_timestamp_file

def import_nijz_dash_labtests():
    filenameByDay = "csv/lab-tests.csv"
    print("Processing", filenameByDay)

    df_existing = pd.read_csv(filenameByDay, index_col='date', parse_dates=['date'])
    print(df_existing)
    d = cepimose.lab_end_timestamp() + timedelta(days=1)

    print(f"Adding/updating lab test data for {d.date()}")

    # copy last row structure, with None values:
    day_data = dict.fromkeys(df_existing.tail(1), None)
    day_data['tests.regular.performed'] = cepimose.lab_PCR_tests_performed() 
    # PCR+HAT day_data['tests.regular.positive'] = cepimose.lab_cases_confirmed()
    day_data['tests.hagt.performed'] = cepimose.lab_HAT_tests_performed()

    day_data['tests.performed'] = day_data['tests.regular.performed']
    # PCR+HAT day_data['tests.positive'] = day_data['tests.regular.positive']

    df_day_data = pd.DataFrame([day_data], index=[d])
    df_day_data.index.name = 'date'
    print(df_day_data)

    df_updated = df_day_data.combine_first(df_existing).fillna(0).round().replace({0: None}).astype('Int64')

    #recalculate .todate fields
    df_updated['tests.regular.performed.todate'] = \
        df_updated['tests.regular.performed'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    df_updated['tests.regular.positive.todate'] = \
        df_updated['tests.regular.positive'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    df_updated['tests.hagt.performed.todate'] = \
        df_updated['tests.hagt.performed'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    df_updated['tests.performed.todate'] = \
        df_updated['tests.performed'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    df_updated['tests.positive.todate'] = \
        df_updated['tests.positive'].fillna(0).cumsum().replace({0: None}).astype('Int64')

    print(df_updated)

    yesterday = date.today() - timedelta(days=1)
    if d.date() < yesterday:
        print(f"ABORTING update with too old date {d.date()} ({d}). Now is {datetime.now()}")
        print(f"Cases {cepimose.lab_cases_confirmed()}, PCR: {cepimose.lab_PCR_tests_performed()} HAT: {cepimose.lab_HAT_tests_performed()}")
        #exit(1)

    old_hash = sha1sum(filenameByDay)
    df_updated.to_csv(filenameByDay, date_format='%Y-%m-%d',line_terminator='\r\n')
    write_timestamp_file(filenameByDay, old_hash)

    return cepimose.lab_cases_confirmed()  # PCR+HAT positive is confirmed cases


if __name__ == "__main__":
    update_time = int(time.time())

    last_day_cases = import_nijz_dash_labtests()
    computeCasesWithCount(update_time, last_day_cases)
    computeStats(update_time)
