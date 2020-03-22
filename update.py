import pathlib
import os

import sheet2csv

SHEET_ID_DEV = "1GDYUsjtJMub8Gh_hZMu4UQw6hAVmtUh6E0rS9dlUl3o"
SHEET_ID_PROD = "1N1qLMoWyi3WFGhIpPFzKsFmVE0IwNP3elb_c18t2DwY"

SHEET_ID = SHEET_ID_PROD

RANGE_STATS = "Podatki!A3:BT"
RAGNE_PATIENTS = "Pacienti!A3:BM"
RANGE_REGIONS = "Kraji!A1:ZZ"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

if __name__ == "__main__":
    pathlib.Path("data/csv").mkdir(parents=True, exist_ok=True)
    try:
        sheet2csv.sheet2csv(
            id=SHEET_ID, range=RANGE_STATS, api_key=GOOGLE_API_KEY, filename="csv/stats.csv",
        )
    except Exception as e:
        print("Failed to import stats.csv")
        raise e
    try:
        sheet2csv.sheet2csv(
            id=SHEET_ID, range=RAGNE_PATIENTS, api_key=GOOGLE_API_KEY, filename="csv/patients.csv",
        )
    except Exception as e:
        print("Failed to import patients.csv")
        raise e
    try:
        sheet2csv.sheet2csv_rotate(
        id=SHEET_ID,
        range=RANGE_REGIONS,
         api_key=GOOGLE_API_KEY,
        key_prefix='region',
        key_cols=[1,0],
        filename="csv/regions.csv"
        )
    except Exception as e:
        print("Failed to import regions.csv")
        raise e
