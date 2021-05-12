#!/usr/bin/env python

import datetime
import time
import pandas as pd
import cepimose
from update_stats import computeStats

from transform.utils import sha1sum, write_timestamp_file

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
    merged['vaccination.janssen.delivered.todate'] = \
        merged['vaccination.janssen.delivered'].fillna(0).cumsum().replace({0: None}).astype('Int64')
    merged['vaccination.delivered.todate'] = merged['vaccination.pfizer.delivered.todate'] \
        .add(merged['vaccination.moderna.delivered.todate'], fill_value=0) \
        .add(merged['vaccination.az.delivered.todate'], fill_value=0) \
        .add(merged['vaccination.janssen.delivered.todate'], fill_value=0).astype('Int64')

    merged = merged.reindex([  # sort
        'vaccination.administered', 'vaccination.administered.todate',
        'vaccination.administered2nd', 'vaccination.administered2nd.todate',
        'vaccination.used.todate',
        'vaccination.delivered.todate',
        'vaccination.pfizer.delivered', 'vaccination.pfizer.delivered.todate',
        'vaccination.moderna.delivered', 'vaccination.moderna.delivered.todate',
        'vaccination.az.delivered', 'vaccination.az.delivered.todate',
        'vaccination.janssen.delivered', 'vaccination.janssen.delivered.todate'
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
    df['vaccination.used.todate'] = df['vaccination.administered.todate'] + df['vaccination.administered2nd.todate']
    # sort cols
    df = df[['vaccination.administered', 'vaccination.administered.todate', 'vaccination.administered2nd', 'vaccination.administered2nd.todate', 'vaccination.used.todate']]
    df = df.astype('Int64')

    # write csv
    old_hash = sha1sum(filename)
    # replace 0 with pd.NA so it does not get written to CSV
    df.replace(0, pd.NA).to_csv(filename, date_format='%Y-%m-%d')
    write_timestamp_file(filename, old_hash)

def import_nijz_dash_vacc_delivered():
    filename = "csv/vaccination-delivered.csv"

    df = pd.DataFrame.from_dict(cepimose.vaccines_supplied_by_manufacturer()).set_index('date').rename(columns=lambda m: f'vaccination.{m}.delivered')

    manufacturersMap = {
        "pfizer":  cepimose.data.Manufacturer.PFIZER,
        "moderna": cepimose.data.Manufacturer.MODERNA,
        "az":      cepimose.data.Manufacturer.AZ,
        "janssen": cepimose.data.Manufacturer.JANSSEN,
    }

    # add more columns
    manufacturers_supplied_used = cepimose.vaccinations_by_manufacturer_supplied_used()
    columns=[]
    for m in manufacturersMap:
        supplied_used = manufacturers_supplied_used[manufacturersMap[m]]
        df_supplied_used=pd.DataFrame.from_dict(supplied_used).rename(columns={
            'supplied': f'vaccination.{m}.delivered.todate',
            'used': f'vaccination.{m}.used.todate',
        }).set_index('date')

        df = df.join(df_supplied_used)
        columns.append(f'vaccination.{m}.delivered')
        # columns.append(f'vaccination.{m}.delivered.todate')
        columns.append(f'vaccination.{m}.used.todate')

    # # sort columns
    df = df[columns]
 
    # write csv
    old_hash = sha1sum(filename)
    # force integer type
    df.fillna(0).round().astype('Int64').replace({0:None}).to_csv(filename, date_format="%Y-%m-%d", line_terminator='\r\n')
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

def import_nijz_dash_vacc_by_region():
    filename = "csv/vaccination-by_region.csv"
    print("Processing", filename)

    df = pd.DataFrame()
    vaccByRegion = cepimose.vaccinations_by_region_by_day()

    # map cepimose regions to sledilnik regions, preserving previous order
    regions = {
        cepimose.data.Region.OBALNOKRASKA: "kp",
        cepimose.data.Region.GORISKA: "ng",
        cepimose.data.Region.PRIMORSKONOTRANJSKA: "po",
        cepimose.data.Region.GORENJSKA: "kr",
        cepimose.data.Region.OSREDNJESLOVENSKA: "lj",
        cepimose.data.Region.JUGOVZHODNASLOVENIJA: "nm",
        cepimose.data.Region.POSAVSKA: "kk",
        cepimose.data.Region.ZASAVSKA: "za",
        cepimose.data.Region.SAVINJSKA: "ce",
        cepimose.data.Region.KOROSKA: "sg",
        cepimose.data.Region.PODRAVSKA: "mb",
        cepimose.data.Region.POMURSKA: "ms",
    }

    # join all regions
    for reg in regions:
        print("Joining {r} ({reg}): {c} rows:".format(r=regions[reg], reg=reg, c=len(vaccByRegion[reg])))
        regData = pd.DataFrame.from_dict(vaccByRegion[reg]).set_index('date')
        regData["first_diff"] = regData["first_dose"].diff()
        regData["second_diff"] = regData["second_dose"].diff()
        regData = regData[['first_diff', 'first_dose', 'second_diff', 'second_dose']]
        regData.rename(inplace=True, columns={
            'first_diff': 'vaccination.region.{}.1st'.format(regions[reg]),
            'first_dose': 'vaccination.region.{}.1st.todate'.format(regions[reg]),
            'second_diff': 'vaccination.region.{}.2nd'.format(regions[reg]),
            'second_dose': 'vaccination.region.{}.2nd.todate'.format(regions[reg]),
        })
        print(regData)
        print(regData.describe())
        df=df.join(regData, how='outer')

    print(df)
    print(df.describe())

    # write csv
    old_hash = sha1sum(filename)
    # force integer type
    df.fillna(0).round().astype('Int64').replace({0:None}).to_csv(filename, date_format="%Y-%m-%d", line_terminator='\r\n')
    write_timestamp_file(filename, old_hash)

def import_nijz_dash_vacc_by_municipalities():
    filename = "csv/vaccination-by_municipality-latest.csv"
    filenameByDay = "csv/vaccination-by_municipality.csv"
    print("Processing", filename)
    print("Processing", filenameByDay)

    municipalities=pd.read_csv("csv/dict-municipality.csv", index_col="id") [["region",  "iso_code", "name", "name_alt", "population" ]]

    # uppercase for easy matching
    municipalities['name_search']=municipalities['name'].str.upper()
    municipalities['name_alt']=municipalities['name_alt'].str.upper()
    municipalities['name_id']=municipalities.index.str.upper()

    for row in cepimose.vaccinations_by_municipalities_share():
        nameNormalized = row.name.upper().replace('-', ' - ')
        mun=municipalities.loc[municipalities['name_search']==nameNormalized]
        if mun is None or mun.empty:
            mun=municipalities.loc[municipalities['name_alt']==nameNormalized]
        if mun is None or mun.empty:
            mun=municipalities.loc[municipalities['name_id']==nameNormalized]
        if mun is None or mun.empty:
            mun=municipalities.loc[municipalities['name_search']==nameNormalized.replace("SV. ", "SVETA ")]

        if mun is None or mun.empty:
            raise Exception(f'No municipality match: {row.name}')

        if len(mun.index) > 1:
            raise Exception(f'{len(mun.index)} municipalities match: {row.name}')

        pop=mun.to_records()[0].population
        if pop != row.population:
            # comment this out if it starts to fail to continue scraping until the population is fixed in dict-municipality.csv
            raise Exception(f'Population mismatch in {row.name}: {pop} (dict-municipality.csv) != {row.population} (NIJZ)')

        # add new columns:
        munId=mun.to_records()[0].id
        municipalities.loc[munId, 'population'] = row.population # overwrite the population with the one from NIJZ, could differ from the one in dict-municipality.csv
        municipalities.loc[munId, '1st.todate'] = row.dose1
        municipalities.loc[munId, '1st.share.todate'] = round(row.share1, 5)
        municipalities.loc[munId, '2nd.todate'] = row.dose2
        municipalities.loc[munId, '2nd.share.todate'] = round(row.share2, 5)


    # trim down extra columns
    municipalities = municipalities[['region', 'iso_code', 'name', 'population', '1st.todate', '1st.share.todate', '2nd.todate', '2nd.share.todate']]
    municipalities['1st.todate']=municipalities['1st.todate'].astype('Int64')
    municipalities['2nd.todate']=municipalities['2nd.todate'].astype('Int64')
    municipalities.dropna(thresh=4, inplace=True)
    print(municipalities)

    old_hash = sha1sum(filename)
    municipalities.to_csv(filename)
    write_timestamp_file(filename, old_hash)

    # daily history
    today_data = {}
    for id, m in municipalities.iterrows():
        fieldPrefix=f'vaccination.region.{m["region"]}.{id}.'
        # today_data[f'{fieldPrefix}population'] = m["population"]
        today_data[f'{fieldPrefix}1st.todate'] = m["1st.todate"]
        # today_data[f'{fieldPrefix}1st.share.todate'] = m["1st.share.todate"]
        today_data[f'{fieldPrefix}2nd.todate'] = m["2nd.todate"]
        # today_data[f'{fieldPrefix}2nd.share.todate'] = m["2nd.share.todate"]

    df_today = pd.DataFrame([today_data], index=[datetime.date.today()])
    df_today.index.name = 'date'
    # print(df_today)
    # uncomment if there's no previous history file:
    # df_today.to_csv(filenameByDay, date_format='%Y-%m-%d')
    # write_timestamp_file(filenameByDay, "")

    df_existing = pd.read_csv(filenameByDay, index_col=0, parse_dates=[0])
    # print(df_existing)

    df_updated = df_today.combine_first(df_existing).fillna(0).round().replace({0: None}).astype('Int64')
    print(df_updated)

    old_hash = sha1sum(filenameByDay)
    df_updated.to_csv(filenameByDay, date_format='%Y-%m-%d')
    write_timestamp_file(filenameByDay, old_hash)


if __name__ == "__main__":
    update_time = int(time.time())

    import_nijz_dash_vacc_administred()
    import_nijz_dash_vacc_delivered()
    import_nijz_dash_vacc_by_age()
    import_nijz_dash_vacc_by_region()
    import_nijz_dash_vacc_by_municipalities()

    computeVaccination(update_time)
    computeStats(update_time)
