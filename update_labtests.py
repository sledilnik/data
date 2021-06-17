#!/usr/bin/env python

from datetime import timedelta
import time
import pandas as pd
import cepimose
from update_stats import computeStats

from transform.utils import sha1sum, write_timestamp_file

def import_nijz_dash_labtests():
    filenameByDay = "csv/lab-tests.csv"
    print("Processing", filenameByDay)

    df_existing = pd.read_csv(filenameByDay, index_col='date', parse_dates=['date'])
    print(df_existing)
    d = cepimose.lab_end_timestamp()
    earlierdate = d - timedelta(days=1)
    print(d, earlierdate)


    # copy last row structure, with None values:
    day_data = dict.fromkeys(df_existing.tail(1), None)
    
    day_data['tests.regular.performed'] = cepimose.lab_PCR_tests_performed() 
    day_data['tests.regular.performed.todate'] = cepimose.lab_PCR_total_tests_performed()

    day_data['tests.regular.positive'] = cepimose.lab_cases_confirmed()
    day_data['tests.regular.positive.todate'] = cepimose.lab_cases_total_confirmed()

    day_data['tests.hagt.performed'] = cepimose.lab_HAT_tests_performed()
    day_data['tests.hagt.performed.todate'] = cepimose.lab_HAT_total_tests_performed()

    day_data['tests.performed'] = day_data['tests.regular.performed']
    day_data['tests.positive'] = day_data['tests.regular.positive']

    if earlierdate in df_existing.index:
        day_earlier_data = df_existing.loc[earlierdate]
        print(day_earlier_data)
        day_data['tests.performed.todate'] = day_data['tests.performed'] + day_earlier_data['tests.performed.todate']
        day_data['tests.positive.todate'] = day_data['tests.positive'] + day_earlier_data['tests.positive.todate']
    
    else:
        #TODO: check for proper calculation:
        day_data['tests.performed.todate'] = day_data['tests.regular.performed.todate']
        day_data['tests.positive.todate'] = day_data['tests.regular.positive.todate']

    df_day_data = pd.DataFrame([day_data], index=[d])
    df_day_data.index.name = 'date'
    print(df_day_data)

    df_updated = df_day_data.combine_first(df_existing).fillna(0).round().replace({0: None}).astype('Int64')
    print(df_updated)

    old_hash = sha1sum(filenameByDay)
    df_updated.to_csv(filenameByDay, date_format='%Y-%m-%d',line_terminator='\r\n')
    write_timestamp_file(filenameByDay, old_hash)


if __name__ == "__main__":
    update_time = int(time.time())

    import_nijz_dash_labtests()
    computeStats(update_time)
