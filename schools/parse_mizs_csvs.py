#!/usr/bin/env python

from datetime import datetime
from operator import itemgetter
import codecs
import csv
import requests
import io
import dateutil.parser
import logging

logger = logging.getLogger(__name__)
dicts = None


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


def get_sledilnik_key(d, mizs_key):
    """
    Return a sledilnik code (ie. OSOKU) for the
    provided MIZS code.
    """
    if d not in dicts:
        logger.warning("Unknown dictionary: {}".format(d))
        return "N/A"

    sledilnik_key = dicts.get(d).get(mizs_key, "N/A")
    if sledilnik_key == "N/A":
        logger.warning(
            "Unknown '{}' key '{}'. Please add it to dicts-schools-values.csv.".format(
                d, mizs_key
            )
        )

    return sledilnik_key


def reformat_dates(date_columns, row):
    """
    Reformat dates (DAT_OD, DAT_DO, DAT_POROCANJA) from a
    human-readable d.m.Y form into the standard YMD form.
    """

    # parse dates
    for i in date_columns:
        date = dateutil.parser.parse(row[i], dayfirst=True).date()

        # the reporting app doen't seem to validate the year field
        # sometimes, typos can happen
        # fix some common ones
        if date.year == 20:
            date = datetime(2020, date.month, date.day).date()
        elif date.year == 2121:
            date = datetime(2021, date.month, date.day).date()
        elif date.year == 2201:
            date = datetime(2021, date.month, date.day).date()

        if date.year < 2020 or date.year > 2021:
            logger.warning("Suspicious date found in line: \n{}\n".format(row))

        if date.year == 3021 or date.year == 2201 or date.year == 2022:
            date = datetime(2021, date.month, date.day)

        row[i] = date

    # do some extra checks on the start and stop dates
    start_date = row[date_columns[0]]
    stop_date = row[date_columns[1]]
    # start date should of course not come after the stop date
    if start_date > stop_date:
        logger.warning(
            "Start date {} is after the stop date {} in line:\n{}".format(
                start_date, stop_date, row
            )
        )
    # both should not be too far into the past nor the future
    now = datetime.now().date()
    if start_date.year < 2020 or (start_date - now).days > 10:
        logger.warning(
            "Weird start date {} found in line: \n{}".format(start_date, row)
        )
    elif stop_date.year < 2020 or (stop_date - now).days > 90:
        logger.warning("Weird stop date {} found in line: \n{}".format(stop_date, row))


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

    # parse attendee (students) and employee data
    attendees = parse_csv(
        # "https://raw.githubusercontent.com/GK-MIZS/covid/main/ucenci.csv"
        "https://podatki.gov.si/dataset/92670859-fae3-4225-adf4-17be511b87d3/resource/e6bce4f3-01cd-4de9-9fc5-7172da14083a/download/ucenci.csv"
    )
    for row in attendees:
        absence = {
            "date": row[10].strftime("%Y-%m-%d"),
            "absent.from": row[8].strftime("%Y-%m-%d"),
            "absent.to": row[9].strftime("%Y-%m-%d"),
            "school_type": get_sledilnik_key("school_type", row[5]),
            "school": row[2],
            "person_type": "A",
            "person_class": get_sledilnik_key("class", row[11]),
            "reason": get_sledilnik_key("reason", row[13]),
        }

        absences.append(absence)

    employees = parse_csv(
        # "https://raw.githubusercontent.com/GK-MIZS/covid/main/zaposleni.csv"
        "https://podatki.gov.si/dataset/92670859-fae3-4225-adf4-17be511b87d3/resource/732cbeb2-41d9-4e22-95dd-362d40ea44fc/download/zaposleni.csv"
    )
    for row in employees:
        absence = {
            "date": row[10].strftime("%Y-%m-%d"),
            "absent.from": row[8].strftime("%Y-%m-%d"),
            "absent.to": row[9].strftime("%Y-%m-%d"),
            "school_type": get_sledilnik_key("school_type", row[5]),
            "school": row[2],
            "person_type": "E",
            "person_class": get_sledilnik_key("position", row[11]),
            "reason": get_sledilnik_key("reason", row[13]),
        }

        absences.append(absence)

    # sort
    absences = sorted(absences, key=itemgetter("date", "school_type", "school"))

    # save
    header = [
        "date",
        "absent.from",
        "absent.to",
        "school_type",
        "school",
        "person_type",
        "person_class",
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
        csvwriter.writerows(absences)


def school_regimes_csv(outfile):
    """
    Parse teching regime changes in particular classes.
    """

    # merge and sort
    # rows = parse_csv("https://raw.githubusercontent.com/GK-MIZS/covid/main/oddelki.csv")
    rows = parse_csv("https://podatki.gov.si/dataset/92670859-fae3-4225-adf4-17be511b87d3/resource/b45823ec-5434-4d96-b61f-ef257babc39b/download/oddelki.csv")

    # transform
    regimes = []
    for row in rows:
        regime = {
            "date": row[10].strftime("%Y-%m-%d"),
            "changed.from": row[8].strftime("%Y-%m-%d"),
            "changed.to": row[9].strftime("%Y-%m-%d"),
            "school_type": get_sledilnik_key("school_type", row[5]),
            "school": row[2],
            "person_class": get_sledilnik_key("class", row[11]),
            "attendees": row[13],
            "regime": get_sledilnik_key("event", row[14]),
            "reason": get_sledilnik_key("event_reason", row[16]),
        }

        regimes.append(regime)

    # sort
    regimes = sorted(regimes, key=itemgetter("date", "school_type", "school"))

    header = [
        "date",
        "changed.from",
        "changed.to",
        "school_type",
        "school",
        "person_class",
        "attendees",
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
        csvwriter.writerows(regimes)


if __name__ == "__main__":
    dicts = load_dicts()

    school_absences_csv("csv/schools-absences.csv")
    school_regimes_csv("csv/schools-regimes.csv")
