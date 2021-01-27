#! /bin/python

from datetime import datetime
from operator import itemgetter
import codecs
import csv
import requests
import io
import dateutil.parser
import logging

logger = logging.getLogger(__name__)

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


def load_dicts(filename="csv/dict-schools-values.csv"):
    """ Load dictionaries. """
    dicts = {}

    with codecs.open(filename, "r", "utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)

        for row in reader:
            if not row:
                continue

            (d, key, value) = row
            if d not in dicts:
                dicts[d] = {}
            dicts[d][key] = value

    return dicts


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
        date = dateutil.parser.parse(row[i], dayfirst=True).date()
        # fix errornous "0020" year entries
        if date.year == 20:
            date = datetime(2020, date.month, date.day)

        if date.year < 2020 or date.year > 2021:
            logger.warning(
                "Suspicious date found in line: \n{}\n".format(", ".join(row))
            )
        row[i] = date.isoformat()


def parse_csv(url):
    """
    Parse the MIZS Covid-19 pupuls (Uc.csv) and school employees (Zap.csv).
    """

    resp = requests.get(url)
    resp.raise_for_status()

    rows = []

    reader = csv.reader(io.StringIO(resp.text), delimiter=",")
    # skip first line
    next(reader)

    date_columns = range(8, 11)
    for row in reader:
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
    attendees = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/ucenci.csv"
    )
    employees = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/zaposleni.csv"
    )
    absences = sorted(attendees + employees, key=itemgetter(10, 7, 1, 3))

    # transform
    new = []
    for row in absences:
        new.append(
            {
                "date": row[10],
                "absent.from": row[8],
                "absent.to": row[9],
                "type": SCHOOL_TYPES.get(row[5], "N/A"),
                "school_id": row[2],
                "subunit": row[12],
                "reason": row[14],
            }
        )

    with open(outfile, "w", encoding="utf-8") as csvfile:
        header = [
            "date",
            "absent.from",
            "absent.to",
            "type",
            "school_id",
            "subunit",
            "reason",
        ]

        csvwriter = csv.DictWriter(
            csvfile,
            fieldnames=header,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        csvwriter.writeheader()
        csvwriter.writerows(new)


if __name__ == "__main__":
    school_absences_csv("csv/school-absences.csv")
