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
    """
    Load the dictionaries needed to translate
    mizs keys to sledilnik keys.
    """
    dicts = {}

    with codecs.open(filename, "r", "utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)

        for row in reader:
            if not row:
                continue

            (d, sledilnik_key, mizs_key, value) = row
            if not value:
                value = mizs_key

            if d not in dicts:
                dicts[d] = {}
            dicts[d][mizs_key] = sledilnik_key

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
    absences = []

    # load mizs key to sledilnik key transformations
    dicts = load_dicts()

    # parse attendee (students) and employee data
    attendees = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/ucenci.csv"
    )
    for row in attendees:
        absences.append(
            {
                "date": row[10],
                "absent.from": row[8],
                "absent.to": row[9],
                "school_type": dicts["KATEGORIJA"].get(row[5], "N/A"),
                "school": row[2],
                "person_type": "attendee",
                "subunit": dicts["ODDELEK"].get(row[11], "N/A"),
                "reason": dicts["VZROK"].get(row[13]),
            }
        )
    employees = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/zaposleni.csv"
    )
    for row in employees:
        # pdb.set_trace()
        absences.append(
            {
                "date": row[10],
                "absent.from": row[8],
                "absent.to": row[9],
                "school_type": dicts["KATEGORIJA"].get(row[5], "N/A"),
                "school": row[2],
                "person_type": "employee",
                "subunit": dicts["DELOVNO_MESTO"].get(row[11], "N/A"),
                "reason": dicts["VZROK"].get(row[13], "N/A"),
            }
        )

    # sort
    absences = sorted(
        absences, key=itemgetter("date", "school_type", "school")
    )  # , "reason"))

    # save
    with open(outfile, "w", encoding="utf-8") as csvfile:
        header = [
            "date",
            "absent.from",
            "absent.to",
            "school_type",
            "school",
            "person_type",
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
        csvwriter.writerows(absences)


def school_regimes_csv(outfile):
    """
    Parse teching regime changes in particular classes.
    """

    # merge and sort
    rows = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/oddelki.csv"
    )

    # load mizs key to sledilnik key transformations
    dicts = load_dicts()

    # transform
    regimes = []
    for row in rows:
        regimes.append(
            {
                "date": row[10],
                "changed.from": row[8],
                "changed.to": row[9],
                "school_type": dicts["KATEGORIJA"].get(row[5], "N/A"),
                "school": row[2],
                "subunit": row[11],
                "students": row[13],
                "regime": dicts["DOGODEK"].get(row[14], "N/A"),
                "reason": dicts["VZROK_DOGODEK"].get(row[16], "N/A"),
            }
        )

    with open(outfile, "w", encoding="utf-8") as csvfile:
        header = [
            "date",
            "changed.from",
            "changed.to",
            "school_type",
            "school",
            "subunit",
            "students",
            "regime",
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
        csvwriter.writerows(regimes)


if __name__ == "__main__":
    school_absences_csv("csv/schools-absences.csv")
    school_regimes_csv("csv/schools-regimes.csv")
