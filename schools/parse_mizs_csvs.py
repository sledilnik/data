#! /bin/python

from datetime import datetime, timedelta
from operator import itemgetter
import codecs
import csv
import requests
import io
import dateutil.parser
import logging

logger = logging.getLogger(__name__)


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
                "Suspicious date found in line: \n{}\n".format(row)
            )
        row[i] = date


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

    for row in reader:
        reformat_dates(range(8, 11), row)
        rows.append(row)

    return rows


def school_absences_csv(outfile):
    """
    Merge confirmed atendee and employee absences by date, school, unit
    """
    absences = []
    absences_current = []

    # load mizs key to sledilnik key transformations
    dicts = load_dicts()

    # parse attendee (students) and employee data
    attendees = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/ucenci.csv"
    )
    for row in attendees:
        absence = {
            "date": row[10].isoformat(),
            "absent.from": row[8].isoformat(),
            "absent.to": row[9].isoformat(),
            "school_type": dicts["KATEGORIJA"].get(row[5], "N/A"),
            "school": row[2],
            "person_type": "attendee",
            "subunit": dicts["ODDELEK"].get(row[11], "N/A"),
            "reason": dicts["VZROK"].get(row[13]),
        }

        absences.append(absence)
        if datetime.now().date() < row[9] + timedelta(days=3):
            absences_current.append(absence)

    employees = parse_csv(
        "https://raw.githubusercontent.com/GK-MIZS/covid/main/zaposleni.csv"
    )
    for row in employees:
        absence = {
            "date": row[10].isoformat(),
            "absent.from": row[8].isoformat(),
            "absent.to": row[9].isoformat(),
            "school_type": dicts["KATEGORIJA"].get(row[5], "N/A"),
            "school": row[2],
            "person_type": "employee",
            "subunit": dicts["DELOVNO_MESTO"].get(row[11], "N/A"),
            "reason": dicts["VZROK"].get(row[13], "N/A"),
        }

        absences.append(absence)
        if row[9] > datetime.now().date() - timedelta(days=30):
            absences_current.append(absence)

    # sort
    absences = sorted(absences, key=itemgetter("date", "school_type", "school"))
    absences_current = sorted(
        absences_current, key=itemgetter("date", "school_type", "school")
    )

    # save
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
    with open(outfile, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.DictWriter(
            csvfile,
            fieldnames=header,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        csvwriter.writeheader()
        csvwriter.writerows(absences_current)

    outfile2 = outfile.replace(".csv", "-archive.csv")
    with open(outfile2, "w", encoding="utf-8") as csvfile:
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
    rows = parse_csv("https://raw.githubusercontent.com/GK-MIZS/covid/main/oddelki.csv")

    # load mizs key to sledilnik key transformations
    dicts = load_dicts()

    # transform
    regimes = []
    regimes_current = []
    for row in rows:
        regime = {
            "date": row[10].isoformat(),
            "changed.from": row[8].isoformat(),
            "changed.to": row[9].isoformat(),
            "school_type": dicts["KATEGORIJA"].get(row[5], "N/A"),
            "school": row[2],
            "subunit": dicts["ODDELEK"].get(row[11], "N/A"),
            "students": row[13],
            "regime": dicts["DOGODEK"].get(row[14], "N/A"),
            "reason": dicts["VZROK_DOGODEK"].get(row[16], "N/A"),
        }

        regimes.append(regime)
        if row[9] > datetime.now().date() - timedelta(days=30):
            regimes_current.append(regime)

    # sort
    regimes = sorted(regimes, key=itemgetter("date", "school_type", "school"))
    regimes_current = sorted(
        regimes_current, key=itemgetter("date", "school_type", "school")
    )

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
    with open(outfile, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.DictWriter(
            csvfile,
            fieldnames=header,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        csvwriter.writeheader()
        csvwriter.writerows(regimes_current)

    outfile2 = outfile.replace(".csv", "-archive.csv")
    with open(outfile2, "w", encoding="utf-8") as csvfile:
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
