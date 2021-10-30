#!/usr/bin/env python

import glob
import logging
import os
from datetime import datetime

import pandas as pd

from country_codes import get_county_code
from utils import sha1sum, write_timestamp_file, download_nijz_xslx_file


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

covid_data_path = os.getenv('COVID_DATA_PATH')
assert covid_data_path, 'COVID_DATA_PATH env variable must be set. (The location of the COVID-DATA folder)'

download_nijz_xslx_file(download_folder=os.path.join(covid_data_path, 'EPI'), search_for='tedenski_prikaz_okuzeni')
download_nijz_xslx_file(download_folder=os.path.join(covid_data_path, 'EPI'), search_for='tedenski_prikaz_umrli')

SOURCE_FILE_INFECTED = max(glob.glob(os.path.join(covid_data_path, 'EPI') + '/tedenski_prikaz_okuzeni*.xlsx'))  # take latest
logger.info(f'SOURCE_FILE okuzeni: {SOURCE_FILE_INFECTED}')
SOURCE_FILE_DECEASED = max(glob.glob(os.path.join(covid_data_path, 'EPI') + '/tedenski_prikaz_umrli*.xlsx'))  # take latest
logger.info(f'SOURCE_FILE umrli: {SOURCE_FILE_DECEASED}')
CSV_FOLDER = os.path.join(os.path.dirname(__file__), '../csv')


df_d_1 = pd.read_excel(io=SOURCE_FILE_DECEASED, sheet_name='Tabela 1', engine='openpyxl', skiprows=[0], skipfooter=2)
df_d_1.drop('Ostalo prebivalstvo', axis='columns', inplace=True)
df_d_1.rename(columns={'Leto in ISO teden izvida': 'week', 'Oskrbovanci': 'week.rhoccupant', 'SKUPAJ': 'week.confirmed'}, inplace=True)
df_d_1.set_index('week', inplace=True)
df_d_1 = df_d_1.replace({0: None}).astype('Int64')

df_d_2 = pd.read_excel(io=SOURCE_FILE_DECEASED, sheet_name='Tabela 2', engine='openpyxl', skiprows=[0], skipfooter=2)
df_d_2.drop('Ostalo prebivalstvo', axis='columns', inplace=True)
df_d_2.rename(columns={'Leto in ISO teden smrti': 'week', 'Oskrbovanci': 'week.deceased.rhoccupant', 'SKUPAJ': 'week.deceased'}, inplace=True)
df_d_2.set_index('week', inplace=True)
df_d_2 = df_d_2.replace({0: None}).astype('Int64')

df_d_3 = pd.read_excel(io=SOURCE_FILE_DECEASED, sheet_name='Tabela 3', engine='openpyxl', skiprows=[0, 2], skipfooter=2)
df_d_3.drop(['Leto, ISO teden in datum smrti', 'SKUPAJ'], axis='columns', inplace=True)
df_d_3 = df_d_3.rename(columns={'Unnamed: 1': 'date', 'Oskrbovanci': 'deceased.rhoccupant.todate', 'Ostalo prebivalstvo': 'deceased.other.todate'}).set_index('date').rename(mapper=lambda x: datetime.strptime(x, '%d.%m.%Y'), axis='rows')
df_d_3 = df_d_3.cumsum()
df_d_3 = df_d_3.replace({0: None}).astype('Int64')

df_d_4 = pd.read_excel(io=SOURCE_FILE_DECEASED, sheet_name='Tabela 4', engine='openpyxl', skiprows=[0, 2], skipfooter=2)
df_d_4.drop(['Leto, ISO teden in datum smrti', 'SKUPAJ'], axis='columns', inplace=True)
df_d_4 = df_d_4.rename(columns={
    'Unnamed: 1': 'date',
    'Pomurska': 'region.ms.todate',
    'Podravska': 'region.mb.todate',
    'Koroška': 'region.sg.todate',
    'Savinjska': 'region.ce.todate',
    'Zasavska': 'region.za.todate',
    'Posavska': 'region.kk.todate',
    'Jugovzhodna Slovenija': 'region.nm.todate',
    'Osrednjeslovenska': 'region.lj.todate',
    'Gorenjska': 'region.kr.todate',
    'Primorsko-notranjska': 'region.po.todate',
    'Goriška': 'region.ng.todate',
    'Obalno-kraška': 'region.kp.todate',
    'TUJINA': 'region.foreign.todate',
    'NEZNANO': 'region.unknown.todate'
}).set_index('date').rename(mapper=lambda x: datetime.strptime(x, '%d.%m.%Y'), axis='rows')
df_d_4 = df_d_4.cumsum()
df_d_4['region.todate'] = df_d_4.sum(axis='columns')
df_d_4 = df_d_4.replace({0: None}).astype('Int64')

df_d_5 = pd.read_excel(io=SOURCE_FILE_DECEASED, sheet_name='Tabela 5', engine='openpyxl', skiprows=[0, 1, 2], skipfooter=2)
df_d_5.drop(['Unnamed: 0', 'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24'], axis='columns', inplace=True)
columns = []
age_ranges = ['0-4', '5-14', '15-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75-84', '85+']
for gender in ['male', 'female']:
    for age_range in age_ranges:
        columns.append(f'deceased.{gender}.{age_range}.todate')
df_d_5.columns = ['date'] + columns
df_d_5.set_index('date', inplace=True)
df_d_5 = df_d_5.rename(mapper=lambda x: datetime.strptime(x, '%d.%m.%Y'), axis='rows')

for age_range in age_ranges:
    df_d_5[f'deceased.{age_range}.todate'] = df_d_5[f'deceased.male.{age_range}.todate'] + df_d_5[f'deceased.female.{age_range}.todate']
df_d_5['deceased.male.todate'] = df_d_5[[f'deceased.male.{age_range}.todate' for age_range in age_ranges]].sum(axis='columns')
df_d_5['deceased.female.todate'] = df_d_5[[f'deceased.female.{age_range}.todate' for age_range in age_ranges]].sum(axis='columns')
df_d_5['deceased.todate'] = df_d_5[[f'deceased.{age_range}.todate' for age_range in age_ranges]].sum(axis='columns')
df_d_5 = df_d_5.reindex([
    'deceased.0-4.todate', 'deceased.5-14.todate', 'deceased.15-24.todate', 'deceased.25-34.todate', 'deceased.35-44.todate',
    'deceased.45-54.todate', 'deceased.55-64.todate', 'deceased.65-74.todate', 'deceased.75-84.todate', 'deceased.85+.todate',
    'deceased.todate', 'deceased.female.0-4.todate', 'deceased.female.5-14.todate', 'deceased.female.15-24.todate',
    'deceased.female.25-34.todate', 'deceased.female.35-44.todate', 'deceased.female.45-54.todate', 'deceased.female.55-64.todate',
    'deceased.female.65-74.todate', 'deceased.female.75-84.todate', 'deceased.female.85+.todate', 'deceased.female.todate',
    'deceased.male.0-4.todate', 'deceased.male.5-14.todate', 'deceased.male.15-24.todate', 'deceased.male.25-34.todate',
    'deceased.male.35-44.todate', 'deceased.male.45-54.todate', 'deceased.male.55-64.todate', 'deceased.male.65-74.todate',
    'deceased.male.75-84.todate', 'deceased.male.85+.todate', 'deceased.male.todate'
], axis='columns')
df_d_5 = df_d_5.cumsum().replace({0: None}).astype('Int64')

df_i_1 = pd.read_excel(io=SOURCE_FILE_INFECTED, sheet_name='Tabela 1', engine='openpyxl', skiprows=[0, 2], skipfooter=1) \
    .rename(columns={
        'Teden': 'week',
        'Skupaj': 'week.investigated',
        'lokalni vir': 'week.src.local',
        'neznani vir': 'week.src.unknown',
        'uvožen': 'week.src.import',
        'uvožen skupek': 'week.src.import-related',
    }).set_index('week').drop('ni podatka', axis='columns')
df_i_1 = df_i_1.replace({0: None}).astype('Int64')

df_i_2 = pd.read_excel(io=SOURCE_FILE_INFECTED, sheet_name='Tabela 2', engine='openpyxl', skiprows=[0, 2], skipfooter=1) \
    .rename(columns={
        'Teden': 'week',
        'družina, skupno gospodinjstvo': 'week.loc.family',
        'delovno mesto': 'week.loc.work',
        'vzgojno-izobraževalni zavod': 'week.loc.school',
        'bolnišnica': 'week.loc.hospital',
        'druga zdravstvena ustanova': 'week.loc.otherhc',
        'DSO/SVZ': 'week.loc.rh',
        'zapor': 'week.loc.prison',
        'javni prevoz': 'week.loc.transport',
        'trgovina': 'week.loc.shop',
        'gostinski obrat': 'week.loc.restaurant',
        'športna dejavnost (zaprt prostor)': 'week.loc.sport',
        'zasebno druženje': 'week.loc.gathering_private',
        'organizirani dogodek': 'week.loc.gathering_organized',
        'drugo': 'week.loc.other',
        'neznano': 'week.loc.unknown'
    }).drop('Skupaj', axis='columns').set_index('week')
df_i_2 = df_i_2.replace({0: None}).astype('Int64')

df_i_3 = pd.read_excel(io=SOURCE_FILE_INFECTED, sheet_name='Tabela 3', engine='openpyxl', skiprows=[0, 2], skipfooter=1).transpose()[:-1]
df_i_3.columns = df_i_3.iloc[0]
df_i_3 = df_i_3[1:]
df_i_3.index.rename('date', inplace=True)
df_i_3 = df_i_3.rename(mapper=lambda x: f'week.from.{get_county_code(x)}', axis='columns')
df_i_3 = df_i_3.replace({0: None}).astype('Int64')

df_i_4 = pd.read_excel(io=SOURCE_FILE_INFECTED, sheet_name='Tabela 4', engine='openpyxl', skiprows=[0, 1, 3], skipfooter=1).rename(columns={
    'Unnamed: 0': 'week',
    'Moški': 'week.healthcare.male',
    'Ženske': 'week.healthcare.female',
    'SKUPAJ': 'week.healthcare'
}).set_index('week').replace({0: None}).astype('Int64')


# source quarantine data from archival CSV
df_quarantine = pd.read_csv(os.path.join(CSV_FOLDER, 'stats-weekly-archive.csv'), index_col='week')
df_quarantine = df_quarantine[['week.sent_to.quarantine', 'week.src.quarantine']]
df_quarantine = df_quarantine.replace({0: None}).astype('Int64')

df_cases_vaccinated = pd.read_csv('csv/cases-vaccinated-weekly.csv', index_col='week')
df_cases_vaccinated = df_cases_vaccinated.astype('Int64')

merged = df_d_1.join([df_d_2, df_i_1, df_i_2, df_i_3, df_i_4, df_quarantine, df_cases_vaccinated])
merged.index.name = 'week'

week_dates = {'week': [], 'date': [], 'date.to': []}
for x in merged.index:
    year, week = x.split('-')
    week_start = datetime.fromisocalendar(int(year), int(week), 1).date()
    week_end = datetime.fromisocalendar(int(year), int(week), 7).date()
    week_dates['week'].append(x)
    week_dates['date'].append(week_start)
    week_dates['date.to'].append(week_end)
merged = merged.join(pd.DataFrame(data=week_dates).set_index('week'))

# new NIJZ files report only from week 23 onwards, take preceeding data from archival CSV
df_archive = pd.read_csv(os.path.join(CSV_FOLDER, 'stats-weekly-archive.csv'), index_col='week')
df_archive = df_archive.iloc[:13]  # keep range 2020-10 to 2020-22
merged.drop([f'2020-{x}' for x in range(10, 23)], axis='rows', inplace=True)
merged = pd.concat([df_archive, merged])

merged = merged.reindex([  # sort
    'date', 'date.to', 'week.hospitalized.vaccinated', 'week.hospitalized.other',
    'week.icu.vaccinated', 'week.icu.vaccinatedpartially', 'week.icu.recovered', 'week.icu.other',
    'week.confirmed', 'week.investigated', 'week.healthcare', 'week.healthcare.male', 'week.healthcare.female', 'week.rhoccupant',
    'week.loc.family', 'week.loc.work', 'week.loc.school', 'week.loc.hospital', 'week.loc.otherhc', 'week.loc.rh', 'week.loc.prison',
    'week.loc.transport', 'week.loc.shop', 'week.loc.restaurant', 'week.loc.sport', 'week.loc.gathering_private',
    'week.loc.gathering_organized', 'week.loc.other', 'week.loc.unknown',
    'week.sent_to.quarantine', 'week.src.quarantine', 'week.src.import', 'week.src.import-related', 'week.src.local', 'week.src.unknown',
    'week.from.aus', 'week.from.aut', 'week.from.aze', 'week.from.bel', 'week.from.bgr', 'week.from.bih', 'week.from.cze', 'week.from.mne',
    'week.from.dnk', 'week.from.dom', 'week.from.est', 'week.from.fra', 'week.from.grc', 'week.from.hrv', 'week.from.irn', 'week.from.ita',
    'week.from.kaz', 'week.from.xkx', 'week.from.hun', 'week.from.mkd', 'week.from.mlt', 'week.from.mar', 'week.from.fsm', 'week.from.deu',
    'week.from.pak', 'week.from.pol', 'week.from.rou', 'week.from.rus', 'week.from.svk', 'week.from.srb', 'week.from.esp', 'week.from.swe',
    'week.from.che', 'week.from.tur', 'week.from.ukr', 'week.from.gbr', 'week.from.usa', 'week.from.are', 'week.from.nld', 'week.from.prt',
    'week.from.lva', 'week.from.alb', 'week.from.cub', 'week.from.mli', 'week.from.egy', 'week.from.tza', 'week.from.fin', 'week.from.nam',
    'week.from.jib', 'week.from.mdv', 'week.from.qat', 'week.from.afg', 'week.from.npl', 'week.from.cyp', 'week.from.mus', 'week.from.tun',
    'week.from.kgz', 'week.from.irl', 'week.from.rwa', 'week.from.zaf', 'week.from.uzb', 'week.from.bwa', 'week.from.gnq', 'week.from.gmb',
    'week.from.ala', 'week.from.lux', 'week.from.abw', 'week.from.wlf', 'week.from.sur', 'week.from.isr', 'week.from.nor'
], axis='columns')



def export_dataframe_to_csv(name: str, dataframe):
    filename = os.path.join(CSV_FOLDER, f'{name}.csv')
    old_hash = sha1sum(filename)
    dataframe.to_csv(filename, line_terminator='\r\n')
    write_timestamp_file(filename=filename, old_hash=old_hash)


export_dataframe_to_csv(name='stats-weekly', dataframe=merged)
export_dataframe_to_csv(name='rh-deceased', dataframe=df_d_3)
export_dataframe_to_csv(name='age-deceased', dataframe=df_d_5)
export_dataframe_to_csv(name='region-deceased', dataframe=df_d_4)
