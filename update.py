import pathlib
import os

import sheet2csv

SHEET_ID_DEV = "1GDYUsjtJMub8Gh_hZMu4UQw6hAVmtUh6E0rS9dlUl3o"
SHEET_ID_PROD = "1N1qLMoWyi3WFGhIpPFzKsFmVE0IwNP3elb_c18t2DwY"

SHEET_ID = SHEET_ID_PROD

RANGE_STATS = "Podatki!A3:ZZ"
RAGNE_PATIENTS = "Pacienti!A3:ZZ"
RANGE_REGIONS = "Kraji!A1:ZZ"
RANGE_HOSPITALS = "Zdr.sistem!A3:ZZ"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


def key_mapper_kraji(values):
  def clean(x):
    return x.lower().replace(" - ", "-").replace(" ", "_").split('/')[0]
  
  keys = list(map( lambda x: '.'.join(['region', clean(x[0]), clean(x[1])]), zip(values[1][1:], values[0][1:])))
  keys.insert(0, 'date')

  return keys, values[2:]

if __name__ == "__main__":
    pathlib.Path("data/csv").mkdir(parents=True, exist_ok=True)
    try:
        sheet2csv.sheet2csv2(id=SHEET_ID, range=RANGE_STATS, api_key=GOOGLE_API_KEY, filename="csv/stats.csv")
    except Exception as e:
        print("Failed to import stats.csv")
        raise e
    try:
        sheet2csv.sheet2csv2(id=SHEET_ID, range=RAGNE_PATIENTS, api_key=GOOGLE_API_KEY, filename='csv/patients.csv')
    except Exception as e:
        print("Failed to import patients.csv")
        raise e
    try:
        values = sheet2csv.sheet2csv2(id=SHEET_ID_PROD, range=RANGE_REGIONS, api_key=GOOGLE_API_KEY, rotate=True, key_mapper=key_mapper_kraji, filename='csv/regions.csv', sort_keys=True)
    except Exception as e:
        print("Failed to import regions.csv")
        raise e
    try:
        values = sheet2csv.sheet2csv2(id=SHEET_ID_PROD, range=RANGE_HOSPITALS, api_key=GOOGLE_API_KEY, filename='csv/hospitals.csv')
    except Exception as e:
        print("Failed to import hospitals.csv")
        raise e
