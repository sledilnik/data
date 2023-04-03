#!/usr/bin/env python
import time
from datetime import date
import pandas as pd

from update_stats import sha1sum, write_timestamp_file
from transform.utils import saveurl

opsi_episari_url="https://podatki.gov.si/dataset/7d73b91a-b551-4783-bb2c-8e4c8953a974/resource/7716561d-3c4e-4522-be4c-493cce35510a/download/episaricsv.csv"
opsi_episari_csv="sources/opsi/episari/episari-opsi.csv"
episari_weekly_csv="csv/episari-nijz-weekly.csv"


def import_opsi_episari():
    saveurl(opsi_episari_url, opsi_episari_csv, "text/csv")


def update_episari_weekly(update_time):
    print("Processing", episari_weekly_csv)
    df_old_hash = sha1sum(episari_weekly_csv)

    df_opsi = pd.read_csv(opsi_episari_csv, sep=';', decimal=',', thousands='.')
    df_opsi.columns = [
        'episari.week',
        'episari.sari.in',
        'episari.tested.in',
        'episari.covid.in',
        'episari.covid.in.vacc.full_6m',
        'episari.covid.in.vacc.other',
        'episari.covid.in.vacc.full_6m.age.65+',
        'episari.covid.in.vacc.unknown',
        'episari.covid.in.notsari',
        'episari.covid.discoveredinhospital',
        'episari.covid.acquiredinhospital',
        'episari.deceased',
        'episari.covid.deceased',
        'episari.all.out',
        'episari.covid.out',
        'episari.sari.icu.in',
        'episari.tested.icu.in',
        'episari.covid.icu.in',
        'episari.covid.in.age.mean',
        'episari.covid.deceased.age.mean',
        'episari.covid.icu.in.age.mean',
        'episari.covid.in.age.00-04',
        'episari.covid.in.age.05-14',
        'episari.covid.in.age.15-24',
        'episari.covid.in.age.25-34',
        'episari.covid.in.age.35-44',
        'episari.covid.in.age.45-54',
        'episari.covid.in.age.55-64',
        'episari.covid.in.age.65-74',
        'episari.covid.in.age.75-84',
        'episari.covid.in.age.85+',
        'episari.covid.icu.in.age.00-04',
        'episari.covid.icu.in.age.05-14',
        'episari.covid.icu.in.age.15-24',
        'episari.covid.icu.in.age.25-34',
        'episari.covid.icu.in.age.35-44',
        'episari.covid.icu.in.age.45-54',
        'episari.covid.icu.in.age.55-64',
        'episari.covid.icu.in.age.65-74',
        'episari.covid.icu.in.age.75-84',
        'episari.covid.icu.in.age.85+',
        'episari.covid.deceased.age.00-04',
        'episari.covid.deceased.age.05-14',
        'episari.covid.deceased.age.15-24',
        'episari.covid.deceased.age.25-34',
        'episari.covid.deceased.age.35-44',
        'episari.covid.deceased.age.45-54',
        'episari.covid.deceased.age.55-64',
        'episari.covid.deceased.age.65-74',
        'episari.covid.deceased.age.75-84',
        'episari.covid.deceased.age.85+' ]
    df_opsi['episari.week'] = df_opsi['episari.week'].str.replace('_','-')
    df_opsi[['year', 'month']] = df_opsi['episari.week'].str.split(pat='-', n=1, expand=True)
    df_opsi['episari.date.from'] = df_opsi.apply(lambda row: date.fromisocalendar(int(row['year']), int(row['month']), 1).isoformat(), axis='columns') 
    df_opsi['episari.date.to'] = df_opsi.apply(lambda row: date.fromisocalendar(int(row['year']), int(row['month']), 7).isoformat(), axis='columns')
    df_opsi.drop(['year', 'month'], axis='columns', inplace=True)
    df_opsi['episari.source'] = 'csv'
    print("OPSI: ", df_opsi)
    
    df_weekly = pd.read_csv(episari_weekly_csv, sep=',') #, index_col='episari.week')
    print("OLD: ", df_weekly)

    df_opsi.drop(df_opsi.loc[df_opsi['episari.date.from'] < '2022-09-26'].index, inplace=True)
    df_weekly.drop(df_weekly.loc[df_weekly['episari.date.from'] >= '2022-09-26'].index, inplace=True)

    merged = pd.concat([df_weekly, df_opsi], ignore_index=True).set_index('episari.date.from')
    merged.to_csv(
        episari_weekly_csv,
        float_format='%.0f',
        lineterminator='\r\n',
        columns = [
            #'episari.date.from',
            'episari.date.to',
            'episari.source',
            'episari.missing',
            'episari.week',
            'episari.sari.in',
            'episari.tested.in',
            'episari.covid.in',
            'episari.covid.in.vacc.full_6m',
            'episari.covid.in.vacc.other',
            'episari.covid.in.vacc.full_6m.age.65+',
            'episari.covid.in.vacc.unknown',
            'episari.covid.in.notsari',
            'episari.covid.discoveredinhospital',
            'episari.covid.acquiredinhospital',
            'episari.deceased',
            'episari.covid.deceased',
            'episari.all.out',
            'episari.covid.out',
            'episari.sari.icu.in',
            'episari.tested.icu.in',
            'episari.covid.icu.in',
            'episari.covid.in.age.mean',
            'episari.covid.deceased.age.mean',
            'episari.covid.icu.in.age.mean',
            'episari.covid.in.age.00-04',
            'episari.covid.in.age.05-14',
            'episari.covid.in.age.15-24',
            'episari.covid.in.age.25-34',
            'episari.covid.in.age.35-44',
            'episari.covid.in.age.45-54',
            'episari.covid.in.age.55-64',
            'episari.covid.in.age.65-74',
            'episari.covid.in.age.75-84',
            'episari.covid.in.age.85+',
            'episari.covid.icu.in.age.00-04',
            'episari.covid.icu.in.age.05-14',
            'episari.covid.icu.in.age.15-24',
            'episari.covid.icu.in.age.25-34',
            'episari.covid.icu.in.age.35-44',
            'episari.covid.icu.in.age.45-54',
            'episari.covid.icu.in.age.55-64',
            'episari.covid.icu.in.age.65-74',
            'episari.covid.icu.in.age.75-84',
            'episari.covid.icu.in.age.85+',
            'episari.covid.deceased.age.00-04',
            'episari.covid.deceased.age.05-14',
            'episari.covid.deceased.age.15-24',
            'episari.covid.deceased.age.25-34',
            'episari.covid.deceased.age.35-44',
            'episari.covid.deceased.age.45-54',
            'episari.covid.deceased.age.55-64',
            'episari.covid.deceased.age.65-74',
            'episari.covid.deceased.age.75-84',
            'episari.covid.deceased.age.85+',
            'episari.covid.in.vacc.3',
            'episari.covid.in.vacc.full',
            'episari.covid.in.vacc.partial',
            'episari.covid.in.vacc.none',
            'episari.covid.in.vacc.none.age.65-84',
            'episari.covid.in.vacc.none.age.85+',
            'episari.covid.in.vacc.3.age.65+',
            'episari.covid.in.vacc.3.age.65-84',
            'episari.covid.in.vacc.3.age.85+',
            'episari.covid.in.vacc.full.age.65+',
            'episari.covid.in.vacc.full.age.65-84',
            'episari.covid.in.vacc.full.age.85+',
            'episari.covid.in.vacc',
            'episari.covid.in.notvacc',
            'episari.covid.in.vacc.age.65+'])
    write_timestamp_file(episari_weekly_csv, df_old_hash)
    print("NEW", merged)


if __name__ == "__main__":
    update_time = int(time.time())

    import_opsi_episari()

    update_episari_weekly(update_time)
