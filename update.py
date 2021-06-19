#!/usr/bin/env python

import datetime
import pathlib
import os
import os.path
import time
import pandas as pd
import sheet2csv

from transform.utils import sha1sum, write_timestamp_file
from update_stats import computeCases, computeMunicipalityCases, computeRegionCases, computeStats


SHEET_HOS = "1jCrsfiJwb_6N39WebN280D3axVvU0Vblk2XpfPI0zMk"
RANGE_PATIENTS = "E:Patients!A3:ZZ"
RANGE_HOSPITALS = "E:Hospitals!A3:ZZ"
RANGE_ICU = "E:ICU!A4:ZZ"

# SHEET_TESTS = "1Mo6D2UlMvGE_-ZtF7aihnqVuUxTIdGGE-tIBBUxj0T0"
# RANGE_LAB_TESTS = "E:LAB-Tests!A3:ZZ"

SHEET_MEAS = "1AzBziQ5ySEaY8cv4NMYfc1LopTWbBRX0hWzMVP8Q52M"
RANGE_SAFETY_MEASURES = "E:Measures!A3:ZZ"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


def import_sheet(update_time, sheet, range, filename, **kwargs):
    print("Processing", filename)
    pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    old_hash = sha1sum(filename)
    try:
        sheet2csv.sheet2csv(id=sheet, range=range, api_key=GOOGLE_API_KEY, filename=filename, **kwargs)
    except Exception as e:
        print("Failed to import {}".format(filename))
        raise e
    write_timestamp_file(filename=filename, old_hash=old_hash)



if __name__ == "__main__":
    update_time = int(time.time())
    import_sheet(update_time, SHEET_MEAS, RANGE_SAFETY_MEASURES, "csv/safety_measures.csv")
    #import_sheet(update_time, SHEET_TESTS, RANGE_LAB_TESTS, "csv/lab-tests.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_PATIENTS, "csv/patients.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_HOSPITALS, "csv/hospitals.csv")
    import_sheet(update_time, SHEET_HOS, RANGE_ICU, "csv/icu.csv")

    computeMunicipalityCases(update_time)
    computeRegionCases(update_time)
    computeCases(update_time)
    computeStats(update_time)

