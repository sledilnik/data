#!/usr/bin/env python
import copy
import csv
import glob
import logging
import os
from datetime import datetime, timedelta

import pandas as pd
# from transform.nijz_daily import export_dataframe_to_csv as daily_export_dataframe_to_csv
# import transform.utils as utils
import requests
import tempfile
import zipfile
import io

def import_google_mobility():
    url = "https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip"
    # local cache for faster/offline development:
    # url = "http://localhost:8080/Region_Mobility_Report_CSVs.zip"
    extension = "_SI_Region_Mobility_Report.csv"
    expectedContentType = "application/zip"

    municipalities=pd.read_csv("csv/dict-municipality.csv", index_col="iso_code") [["region", "id"]]
    # municipalities.set_index("iso_code")
    print(municipalities)

    print("Downloading", url)
    r = requests.get(url, allow_redirects=True, stream=True)
    r.raise_for_status()

    actualContentType = r.headers['Content-Type']
    if actualContentType != expectedContentType:
        raise Exception("Unexpected content-type:", actualContentType)

    z = zipfile.ZipFile(io.BytesIO(r.content))
    listOfFileNames = z.namelist()
    for fileName in listOfFileNames:
        if fileName.endswith(extension):
            print('Reading:', fileName)
            df = pd.read_csv(io.BytesIO(z.read(fileName)), parse_dates=['date'])

            # check if there was something else read for some reason:
            forbiddenMatches = df.loc[df["country_region_code"] != "SI"]
            if len(forbiddenMatches) != 0:
                raise Exception("Unexpected rows with SI:", forbiddenMatches)

            forbiddenMatches = df.loc[df["country_region"] != "Slovenia"]
            if len(forbiddenMatches) != 0:
                raise Exception("Unexpected rows with Slovenia:", forbiddenMatches)

            # Remove empty columns
            df.dropna(how='all', axis=1, inplace=True)

            # Remove irrelevant columns
            del df['country_region_code'] # SI
            del df['country_region']      # Slovenia
            del df['place_id']            # Google-specific
            del df['sub_region_1']        # English administrative unit (upravna enota) name
            del df['sub_region_2']        # English municipality name, iso_3166_2_code is enough for us to match
            # del df['metro_area']          # US-specific
            # del df['census_fips_code']    # US-specific
            # del df['census_fips_code']    # US-specific

            # keep just records for municipalities
            df.dropna(subset=['iso_3166_2_code'], inplace=True)
            # TODO: fix it to keep aggregated country-level data

            # shorten the names
            df.rename(columns=lambda x: x.replace("_percent_change_from_baseline", ""), inplace=True)

            # df.join(municipalities, on="iso_3166_2_code", how="inner")

            # df.set_index(["date", "iso_3166_2_code"], inplace=True)
            df.set_index(["date"], inplace=True)

            # pd.set_option('display.max_rows', None)
            print(df)#.astype('Int64'))

            # TODO: Transform data into whatever shape needed
            # dates = df.index.unique()#.sort()
            # dfnew = pd.DataFrame({'date': dates})
            # dfnew = dfnew.set_index('date')

            # fields=["retail_and_recreation",
            #         "grocery_and_pharmacy",
            #         "parks",
            #         "transit_stations",
            #         "workplaces",
            #         "residential"]
            
            # for miso, m in municipalities.iterrows():
            #     munirows = df.loc[df["iso_3166_2_code"] == miso]
            #     print(miso)
            #     print(m)
            #     print(munirows)
            #     for d, r in munirows.iterrows():
            #         fieldPrefix=f'{m["region"]}.{m["id"]}.'
            #         for f in fields:
            #             dfnew[f'{fieldPrefix}{f}'] = "" #r[f]

            # print(dfnew)

    # TODO: join/merge dataframes into one datafame
    
    # TODO: Save to csv/google-mobility.csv


if __name__ == "__main__":
    import_google_mobility()
