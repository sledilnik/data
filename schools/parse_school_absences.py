#! /bin/python

from operator import itemgetter
from datetime import datetime
import codecs
import csv
import requests
import io
import dateutil.parser

# KAT_MAT/KATEGORIJA (Iz Šifrant_kategorij.xslx)
SCHOOL_TYPES = {
    "1010": "PV",  # Vrtec
    "2010": "OŠ",  # Osnovna šola
    "2020": "OŠPP",  # Osnovna šola za učence s posebnimi potrebami
    "2030": "GŠ",  # Glasbena šola
    "3010": "SŠ",  # Srednja šola
    "3020": "DD",  # Dijaški dom
    "4010": "ZAV",  # Zavodi za otroke in mladostnike s posebnimi potrebami
    "5040": "VSS",  # Višja strokovna šola
}

# School unit (ZAVNAZ) fixes (parts to remove)
UNIT_REMOVE = [
    "Osnovna šola Antona Globočnika",
    "Osnovna šola Destrnik",
    "Osnovna šola Frana Kocbeka Gornji grad",
    "Osnovna šola Miroslava Vilharja",
    "Osnovna šola Ob Dravinji",
    "Osnovna šola Pohorskega odreda Slov. Bistrica",
    "Osnovna šola Sava Kladnika",
    "Osnovna šola dr. Janeza Mencingerja Boh. Bistrica",
    "VIZ II.OŠ Rogaška Slatina",
]

# School unit (Zavnaz) manual fixes
UNIT_FIXES = {}


def reformat_unit(row):
    """
        Remove the main school from the school unit field if present.
        We just want the unit name there.
    """

    # if the unit has the same id as the school
    if row[0] == row[2]:
        row[3] = ""

    # if unit in school
    if row[1] in row[3]:
        # remove school from unit
        row[3] = row[3].replace(row[1], "")
        # capitalize first letter since it might be lowercase now
        if len(row[3]) >= 2:
            row[3] = row[3][0].upper() + row[3][1:]

    # fix some additional mistakes
    for mistake in UNIT_REMOVE:
        if row[3].startswith(mistake):
            row[3] = row[3].replace(mistake, "")
    for mistake, fix in UNIT_FIXES.items():
        if row[3] == mistake:
            row[3] == fix

    # trim
    if row[3].startswith(", "):
        row[3] = row[3].replace(", ", "", 1)
    row[3] = row[3].strip(" ")


def reformat_dates(date_columns, row):
    """
    Reformat the dates from a human-readable d.m.Y form into
    the standard YMD form.
    """
    for i in date_columns:
        date = dateutil.parser.parse(row[i], dayfirst=True)
        row[i] = date.strftime("%Y-%m-%d")


def parse_csv(url):
    """
    Parse the MIZS Covid-19 pupuls (Uc.csv) and school employees (Zap.csv).
    """

    resp = requests.get(url)
    resp.raise_for_status()

    rows = []

    reader = csv.reader(io.StringIO(resp.text), delimiter=",")

    date_columns = range(8, 11)
    for row in reader:
        if not row or row[0].startswith("ZAVSIF"):
            continue

        reformat_unit(row)
        reformat_dates(date_columns, row)
        rows.append(row)

    # sort by reporting date (the last date column)
    rows = sorted(rows, key=itemgetter(date_columns[-1]))
    return rows


def school_absences_csv(outfile):
    """
    Merge confirmed atendee and employee absences by date, school, unit"
    """
    # merge and sort
    attendees = parse_csv("https://raw.githubusercontent.com/GK-MIZS/covid/main/ucenci.csv")
    employees = parse_csv("https://raw.githubusercontent.com/GK-MIZS/covid/main/zaposleni.csv")
    absences = sorted(attendees + employees, key=itemgetter(10, 7, 1, 3))

    # transform
    new = []
    for a in absences:
        school_type = SCHOOL_TYPES.get(a[5], "N/A")  # KATEGORIJA
        municipality = a[7]  # OBCINA
        school_id = a[0]
        school = a[1]  # ZAVMATNAZ
        unit = a[3]  # ZAVNAZ
        subunit = a[12]  # OBDOBJE
        description = a[14]  # VZROK

        row = [
            a[10],
            a[8],
            a[9],
            municipality,
            school_type,
            school_id,
            school,
            unit,
            subunit,
            description,
        ]
        new.append(row)

    with codecs.open(outfile, "w", "utf-8") as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        header = [
            "date",
            "absent.from",
            "absent.to",
            "municipality",
            "type",
            "school_id",
            "school",
            "unit",
            "subunit",
            "reason",
        ]
        csvwriter.writerow(header)
        for row in new:
            csvwriter.writerow(row)


if __name__ == "__main__":
    school_absences_csv("csv/school-absences.csv")
