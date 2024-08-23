#!/usr/bin/env python

import time
from datetime import date, datetime, timedelta
import pandas as pd
import cepimose
from update_stats import computeStats, computeCasesWithCount

from transform.utils import sha1sum, write_timestamp_file, saveurl 

def import_nijz_dash_labtests():
    filenameByDay = "csv/lab-tests.csv"
    print("Processing", filenameByDay)

    df_existing = pd.read_csv(filenameByDay, index_col='date', parse_dates=['date'])
    print(df_existing)
    d = cepimose.lab_end_timestamp()

    print(f"Adding/updating lab test data for {d.date()}")

    # copy last row structure, with None values:
    day_data = dict.fromkeys(df_existing.tail(1), None)
    day_data['tests.regular.performed'] = cepimose.lab_PCR_tests_performed() 
    # PCR+HAT day_data['tests.regular.positive'] = cepimose.lab_cases_confirmed()
    day_data['tests.hagt.performed'] = cepimose.lab_HAT_tests_performed()

    day_data['tests.performed'] = cepimose.lab_PCR_tests_performed()
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
        print(f"SKIP dashboard update: too old date {d.date()} ({d}). Now is {datetime.now()}")
        print(f"Cases {cepimose.lab_cases_confirmed()}, PCR: {cepimose.lab_PCR_tests_performed()} HAT: {cepimose.lab_HAT_tests_performed()}")
        return None

    old_hash = sha1sum(filenameByDay)
    df_updated.to_csv(filenameByDay, date_format='%Y-%m-%d',lineterminator='\r\n')
    write_timestamp_file(filename=filenameByDay, old_hash=old_hash)

    return cepimose.lab_cases_confirmed()  # PCR+HAT positive is confirmed cases



def import_opsi_labtests():
    # https://podatki.gov.si/dataset/dnevno-spremljanje-okuzb-covid-19
    saveurl("https://podatki.gov.si/dataset/56a1a649-5201-46d2-b503-03c6b36a6ee7/resource/9f297da4-1a93-4f62-8c14-cfff5c5d7377/download/vwlusyokuzeni.csv", "csv/cases-opsi.csv", "text/csv")
    saveurl("https://podatki.gov.si/dataset/56a1a649-5201-46d2-b503-03c6b36a6ee7/resource/b2fee4c1-f579-4f6d-8d54-7a1b8755e970/download/covid19potrjeniprimeri.csv", "csv/cases-opsi-light.csv", "text/csv")

    # Update cases from cases-opsi to fill gaps done with dashboard
    df_opsi = pd.read_csv("csv/cases-opsi.csv")
    df_opsi.rename(columns={'datum_izvida': 'date'}, inplace=True)
    # drop tests before first positive cases: NIJZ counted all on that day, we have better data from IMI
    df_opsi.drop(df_opsi.loc[df_opsi['date'] <= '2020-03-04'].index, inplace=True)
    
    filename = 'csv/lab-tests.csv'
    print("Processing", filename)
    df_tests = pd.read_csv(filename, index_col='date')
    df_tests_old_hash = sha1sum(filename)

    df_updated = df_tests.merge(df_opsi[['date', 'stevilo_potrjenih_pcr', 'stevilo_potrjenih_hagt', 'stevilo_testiranj_pcr', 'stevilo_testiranj_hagt']], on='date', how='left')
    df_updated['tests.performed'] = df_updated['stevilo_testiranj_pcr'].combine_first(df_updated['tests.performed'])
    df_updated['tests.performed.todate'] = df_updated['tests.performed'].cumsum()
    df_updated['tests.positive'] = df_updated['stevilo_potrjenih_pcr'].combine_first(df_updated['tests.positive'])
    df_updated['tests.positive.todate'] = df_updated['tests.positive'].cumsum()
    df_updated['tests.regular.performed'] = df_updated['stevilo_testiranj_pcr'].combine_first(df_updated['tests.regular.performed'])
    df_updated['tests.regular.performed.todate'] = df_updated['tests.regular.performed'].cumsum()
    df_updated['tests.regular.positive'] = df_updated['stevilo_potrjenih_pcr'].combine_first(df_updated['tests.regular.positive'])
    df_updated['tests.regular.positive.todate'] = df_updated['tests.regular.positive'].cumsum()
    df_updated['tests.hagt.performed'] = df_updated['stevilo_testiranj_hagt'].combine_first(df_updated['tests.hagt.performed'])
    df_updated['tests.hagt.performed.todate'] = df_updated['tests.hagt.performed'].cumsum()
    df_updated['tests.hagt.positive'] = df_updated['stevilo_potrjenih_hagt'].combine_first(df_updated['tests.hagt.positive'])
    df_updated['tests.hagt.positive.todate'] = df_updated['tests.hagt.positive'].cumsum()
    df_updated.drop(columns=['stevilo_potrjenih_pcr', 'stevilo_potrjenih_hagt', 'stevilo_testiranj_pcr', 'stevilo_testiranj_hagt'], inplace=True)
    df_updated.set_index('date', inplace=True)
    df_updated.replace({0: None}).astype('Int64').to_csv(filename, date_format='%Y-%m-%d',lineterminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=df_tests_old_hash)

    filename = 'csv/cases.csv'
    print("Processing", filename)
    df_cases = pd.read_csv(filename, index_col='date')
    df_cases_old_hash = sha1sum(filename)

    df_updated = df_cases.merge(df_opsi[['date', 'stevilo_potrjenih_skupaj']], on='date', how='outer')
    df_updated.sort_values(by='date', inplace=True)
    df_updated['cases.confirmed'] = df_updated['stevilo_potrjenih_skupaj'].combine_first(df_updated['cases.confirmed'])
    df_updated['cases.confirmed.todate'] = df_updated['cases.confirmed'].cumsum()
    df_updated['cases.active'] = df_updated['cases.confirmed'].rolling(window=14).sum()
    df_updated['cases.closed.todate'] = df_updated['cases.confirmed.todate'] - df_updated['cases.active']
    df_updated.drop(columns=['stevilo_potrjenih_skupaj'], inplace=True)
    df_updated.set_index('date', inplace=True)
    df_updated.replace({0: None}).astype('Int64').to_csv(filename, lineterminator='\r\n')

    write_timestamp_file(filename=filename, old_hash=df_cases_old_hash)



if __name__ == "__main__":
    update_time = int(time.time())

    last_day_cases = import_nijz_dash_labtests()

    import_opsi_labtests()

    if last_day_cases: 
        computeCasesWithCount(update_time, last_day_cases)

    computeStats(update_time)
