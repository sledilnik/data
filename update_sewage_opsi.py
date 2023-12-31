#!/usr/bin/env python
import time
from datetime import date
import pandas as pd

from update_stats import sha1sum, write_timestamp_file
from transform.utils import saveurl

opsi_sewage_url="https://podatki.gov.si/dataset/1b72495b-a13c-4c5f-9c3c-c99c83570998/resource/5f546967-f6e8-4807-a928-4c5f2a3f8e59/download/ocenjenostokuzenihosebssarscov2.csv"
opsi_genome_url="https://podatki.gov.si/dataset/1b72495b-a13c-4c5f-9c3c-c99c83570998/resource/0555e8e9-4462-44ee-a0b7-fa1d8c11ecfa/download/delezimutacijgenomasarscov2.csv"
opsi_sewage_csv="sources/opsi/sewage/sewage-cases-opsi.csv"
opsi_genome_csv="sources/opsi/sewage/sewage-genome-opsi.csv"
sewage_cases_csv="csv/sewage-cases.csv"
sewage_genome_csv="csv/sewage-genome.csv"


def convert_region(region: str):
    return {
        'Pomurska': 'ms',
        'Podravska': 'mb',
        'Koroška': 'sg',
        'Savinjska': 'ce',
        'Zasavska': 'za',
        'Posavska': 'kk',
        'Jugovzhodna Slovenija': 'nm',
        'Osrednjeslovenska': 'lj',
        'Gorenjska': 'kr',
        'Primorsko-notranjska': 'po',
        'Goriška': 'ng',
        'Obalno-kraška': 'kp',
    }.get(region, 'unknown')  # if there's no match we assume it's a date column

def fix_ratio(ratio: float):
    if ratio < 1:
        return ratio
    else:
        return ratio/1000

def underscore_to_space(text: str):
    return text.replace('_', ' ')


def import_opsi_sewage():
    saveurl(opsi_sewage_url, opsi_sewage_csv, "text/csv")
    saveurl(opsi_genome_url, opsi_genome_csv, "text/csv")


def update_sewage_cases(update_time):
    print("Processing", sewage_cases_csv)
    df_old_hash = sha1sum(sewage_cases_csv)

    df_opsi = pd.read_csv(opsi_sewage_csv, sep=',', decimal='.').rename(columns={
        'datum': 'sewage.date',
        'WWTP': 'sewage.station',
        'flow': 'sewage.flow',
        'conc_SARS_N3_raw': 'sewage.n3-raw',
        'COD': 'sewage.cod',
        'norm_vl_SARS_N3': 'sewage.n3-norm',
        'estimated': 'sewage.cases.estimated',
        'aktivni_100.000': 'sewage.cases.active100k',
        'ime_protokol': 'sewage.protocol',
        'lat': 'sewage.lat',
        'lng': 'sewage.lon',
        'Statistična_regija': 'sewage.region',
        'preb_2022H2': 'sewage.population',
        'Delež.preb..priključen.na.ČN': 'sewage.coverage-ratio'})
    df_opsi.drop(columns=['sewage.protocol'], inplace=True) # Drop new, unknown column for nicer diffs until we know what it means and how to use it
    df_opsi['sewage.station'] = df_opsi['sewage.station'].apply(underscore_to_space)
    df_opsi['sewage.region'] = df_opsi['sewage.region'].apply(convert_region)
    df_opsi['sewage.coverage-ratio'] = df_opsi['sewage.coverage-ratio'].apply(fix_ratio)
    df_opsi = df_opsi.set_index(['sewage.date', 'sewage.station'], verify_integrity=True)
    df_opsi = df_opsi.sort_values(by=['sewage.date','sewage.station'], ascending=True)

    print("CASES: ", df_opsi)
    
    df_opsi.to_csv(sewage_cases_csv, lineterminator='\r\n') 
    write_timestamp_file(sewage_cases_csv, df_old_hash)


def update_sewage_genome(update_time):
    print("Processing", sewage_genome_csv)
    df_old_hash = sha1sum(sewage_genome_csv)

    df_opsi = pd.read_csv(opsi_genome_csv, sep=',', decimal='.').rename(columns={
        'datum': 'sewage.date',
        'WWTP': 'sewage.station',
        'Različica.virusa': 'sewage.genome',
        'Delež.različice': 'sewage.ratio',
        'Statistična_regija': 'sewage.region'})
    df_opsi = df_opsi[['sewage.date', 'sewage.station', 'sewage.genome', 'sewage.ratio', 'sewage.region']] # reorder columns for readable diffs
    df_opsi['sewage.station'] = df_opsi['sewage.station'].apply(underscore_to_space)
    df_opsi['sewage.region'] = df_opsi['sewage.region'].apply(convert_region)
    df_opsi['sewage.ratio'] = df_opsi['sewage.ratio'].apply(fix_ratio)
    df_opsi = df_opsi.dropna(subset='sewage.date')
    df_opsi = df_opsi.set_index(['sewage.date', 'sewage.station', 'sewage.genome'], verify_integrity=True)
    df_opsi = df_opsi.sort_values(by=['sewage.date', 'sewage.station', 'sewage.genome'], ascending=True)

    print("GENOME: ", df_opsi)
    
    df_opsi.to_csv(sewage_genome_csv, lineterminator='\r\n') 
    write_timestamp_file(sewage_genome_csv, df_old_hash)


if __name__ == "__main__":
    update_time = int(time.time())

    import_opsi_sewage()

    update_sewage_cases(update_time)
    update_sewage_genome(update_time)
