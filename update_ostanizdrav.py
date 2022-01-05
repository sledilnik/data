#!/usr/bin/env python
import time
from datetime import date
from numpy import int64, inf, nan
from pandas.core.indexes.base import Index 
import requests
import pandas as pd

from update_stats import sha1sum, write_timestamp_file #, computeStats

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


def import_opsi_ostanizdrav():
    # https://podatki.gov.si/dataset/statisticni-podatki-aplikacije-ostanizdrav
    saveurl("https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/f8711982-df42-48e6-9c07-92fcb89cb15c/download/prenosiandroid.csv", "ostanizdrav/podatki.gov.si/prenosiandroid.csv", "text/csv")
    saveurl("https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/1786b9c7-def2-40f0-bccf-7866b5878ef5/download/iosprenosi.csv", "ostanizdrav/podatki.gov.si/iosprenosi.csv", "text/csv")
    saveurl("https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/406b4306-cf45-4d49-b44e-48c8b4c1de78/download/tanstatistika.csv", "ostanizdrav/podatki.gov.si/tanstatistika.csv", "text/csv")
    saveurl("https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/1167a46b-22ac-455f-b134-fedaf258ea0d/download/tanvneseno.csv", "ostanizdrav/podatki.gov.si/tanvneseno.csv", "text/csv")
    saveurl("https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/3710deae-85c9-41e5-ab27-cb06f6f74533/download/agregacijaostanizdrav.json", "ostanizdrav/podatki.gov.si/agregacijaostanizdrav.json", "application/json")

    # https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav
    saveurl("https://www.gov.si/assets/ministrstva/MJU/devices.csv", "ostanizdrav/gov.si/devices.csv", "text/csv")


def merge_ostanizdrav():
    filename = 'csv/ostanizdrav.csv'
    print("Processing", filename)
    old_file_hash = sha1sum(filename)

    df_dl_android = pd.read_csv('ostanizdrav/podatki.gov.si/prenosiandroid.csv',
        index_col='Datum',
        parse_dates=['Datum'],
        date_parser=lambda date_string: pd.to_datetime(date_string, format="%d.%m.%Y"),
        dtype={'Pridobivanje uporabnikov': 'int64'}
        ).sort_index()
    df_dl_android.rename(columns={'Pridobivanje uporabnikov':'dl.android'}, inplace=True)
    df_dl_android.index.rename('date', inplace=True)
    df_dl_android['dl.android.todate'] = df_dl_android['dl.android'].fillna(0).cumsum()
    # print(df_dl_android)


    df_dl_ios = pd.read_csv('ostanizdrav/podatki.gov.si/iosprenosi.csv',
        index_col='Datum',
        parse_dates=['Datum'],
        date_parser=lambda date_string: pd.to_datetime(date_string, format="%d.%m.%Y"),
        dtype={'Pridobivanje uporabnikov': 'int64'}
        ).sort_index()
    df_dl_ios.rename(columns={'Pridobivanje uporabnikov':'dl.ios'}, inplace=True)
    df_dl_ios.index.rename('date', inplace=True)
    df_dl_ios['dl.ios.todate'] = df_dl_ios['dl.ios'].fillna(0).cumsum()
    # print(df_dl_ios)


    merged = df_dl_android.join(df_dl_ios, how='outer').fillna(0)
    merged['dl.todate'] = merged['dl.android.todate'] + merged['dl.ios.todate']
    # print(merged)


    # MJU started to publish with 2020-09-25
    df_tan_issued = pd.read_csv('ostanizdrav/podatki.gov.si/tanstatistika.csv',
        index_col='created_at',
        parse_dates=['created_at'],
        date_parser=lambda date_string: pd.to_datetime(date_string, format="%d.%m.%Y"),
        dtype={'count': 'int64'}
        ).sort_index()
    df_tan_issued.rename(columns={'count':'tan.issued'}, inplace=True)
    df_tan_issued.index.rename('date', inplace=True)
    df_tan_issued['tan.issued.todate'] = df_tan_issued['tan.issued'].fillna(0).cumsum()
    # print(df_tan_issued)

    merged = merged.join(df_tan_issued, how='outer').fillna(0)


    # early guestimates via corona tracker tracker (https://github.com/sledilnik/ctt)
    df_tan_entered_ctt = pd.read_json('ostanizdrav/ctt/data.json')
    df_tan_entered_ctt = df_tan_entered_ctt[['date','users_published']]
    df_tan_entered_ctt.set_index('date', inplace=True)
    df_tan_entered_ctt = df_tan_entered_ctt.truncate(after=pd.Timestamp('2021-02-09')) # after this date EU key exchange started to spoil the metrics
    df_tan_entered_ctt.dropna()
    df_tan_entered_ctt.rename(columns={'users_published':'tan.entered'}, inplace=True)
    # print(df_tan_entered_ctt)

    # MJU started to publish on 2021-04-07
    df_tan_entered = pd.read_csv('ostanizdrav/podatki.gov.si/tanvneseno.csv',
        index_col='created_at',
        parse_dates=['created_at'],
        date_parser=lambda date_string: pd.to_datetime(date_string, format="%d.%m.%Y"),
        dtype={'count': 'int64'}
        ).sort_index()
    df_tan_entered.rename(columns={'count':'tan.entered'}, inplace=True)
    df_tan_entered.index.rename('date', inplace=True)

    # combine them, with some gap between them
    df_tan_entered = pd.concat([df_tan_entered_ctt, df_tan_entered])
    df_tan_entered['tan.entered.todate'] = df_tan_entered['tan.entered'].fillna(0).cumsum()
    # print(df_tan_entered)

    merged = merged.join(df_tan_entered, how='outer').fillna(0)
    merged['tan.ratio_entered_issued'] = merged['tan.entered'] / merged['tan.issued']
    merged.replace(inf, nan, inplace=True) #remove infinity from period before we have data for tan.issued


    df_cases = pd.read_csv('csv/cases.csv',
        index_col='date',
        parse_dates=['date'],
        usecols=['date','cases.confirmed'],
        # dtype={'cases.confirmed': 'int64'}
        ).sort_index()
    # print(df_cases)

    merged = merged.join(df_cases, how='inner').fillna(0)
    merged['tan.ratio_entered_cases'] = merged['tan.entered'] / merged['cases.confirmed']
    merged['tan.ratio_issued_cases'] = merged['tan.issued'] / merged['cases.confirmed']


    # recalculate .todate for whole dataset
    merged['dl.android.todate'] = merged['dl.android'].fillna(0).cumsum()
    merged['dl.ios.todate'] = merged['dl.ios'].fillna(0).cumsum()
    merged['dl.todate'] = merged['dl.android.todate'] + merged['dl.ios.todate']
    merged['tan.entered.todate'] = merged['tan.entered'].fillna(0).cumsum()

    merged = merged.round({
        'tan.ratio_entered_issued': 3,
        'tan.ratio_entered_cases': 3,
        'tan.ratio_issued_cases': 3,
        })
    merged = merged.astype({
        'dl.android': int64,
        'dl.android.todate': int64,
        'dl.ios': int64,
        'dl.ios.todate': int64,
        'dl.todate': int64,
        'tan.issued': int64,
        'tan.issued.todate': int64,
        'tan.entered': int64,
        'tan.entered.todate': int64,
        'cases.confirmed': int64,
        })
    # print(merged)

    merged.replace({0: None}).to_csv(filename)
    write_timestamp_file(filename=filename, old_hash=old_file_hash)


if __name__ == "__main__":
    update_time = int(time.time())

    import_opsi_ostanizdrav()
    merge_ostanizdrav()
