#!/usr/bin/env python

"""
  Prepare daily covid-19 case summaries for schools
"""

import codecs
import csv
import requests

def school_cases_csv(outfile):
    
    rows = []
    # rows.append(header)

    resp = requests.get('https://raw.githubusercontent.com/GK-MIZS/covid/main/api.json')
    resp.raise_for_status()

    j = resp.json()

    updates = j[1:]

    cases_confirmed_todate = 0
    quarantines_confirmed_todate = 0
    cases_confirmed_todate_attendees = 0
    cases_confirmed_todate_employees = 0
    for u in updates:
        cases_confirmed = (
            u["ucenci_okuzbe_nove"]["Osnovna_sola"]
            + u["ucenci_okuzbe_nove"]["Osnovna_sola_s_prilagojenim_programom"]
            + u["zaposleni_okuzbe_nove"]["Osnovna_sola"]
            + u["zaposleni_okuzbe_nove"]["Osnovna_sola_s_prilagojenim_programom"]
        )
        cases_confirmed_todate += cases_confirmed
        cases_active = (
            u["ucenci_okuzbe_aktivne"]["Osnovna_sola"]
            + u["ucenci_okuzbe_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
            + u["zaposleni_okuzbe_aktivne"]["Osnovna_sola"]
            + u["zaposleni_okuzbe_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
        )

        quarantines_confirmed = (
            u["ucenci_v_karanteni_novi"]["Osnovna_sola"]
            + u["ucenci_v_karanteni_novi"]["Osnovna_sola_s_prilagojenim_programom"]
        )
        quarantines_confirmed_todate += quarantines_confirmed
        quarantines_active = (
            u["ucenci_v_karanteni_aktivne"]["Osnovna_sola"]
            + u["ucenci_v_karanteni_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
        )

        cases_confirmed_attendees = (
            u["ucenci_okuzbe_nove"]["Osnovna_sola"]
            + u["ucenci_okuzbe_nove"]["Osnovna_sola_s_prilagojenim_programom"]
        )
        cases_confirmed_todate_attendees += cases_confirmed_attendees
        cases_active_attendees = (
            u["ucenci_okuzbe_aktivne"]["Osnovna_sola"]
            + u["ucenci_okuzbe_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
        )

        cases_confirmed_employees = (
            u["zaposleni_okuzbe_nove"]["Osnovna_sola"]
            + u["zaposleni_okuzbe_nove"]["Osnovna_sola_s_prilagojenim_programom"]
        )
        cases_confirmed_todate_employees += cases_confirmed_employees
        cases_active_employees = (
            u["zaposleni_okuzbe_aktivne"]["Osnovna_sola"]
            + u["zaposleni_okuzbe_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
        )

        rows.append(
            {
                "date": "{}-{}-{}".format(u["year"], u["month"], u["day"]),
                "cases.confirmed.todate": cases_confirmed_todate,
                "cases.active": cases_active,
                "quarantine.confirmed.todate": quarantines_confirmed_todate,
                "quarantine.active": quarantines_active,
                "cases.attendees.confirmed.todate": cases_confirmed_todate_attendees,
                "cases.attendees.active": cases_active_attendees,
                "cases.employees.confirmed.todate": cases_confirmed_todate_employees,
                "cases.employees.active": cases_active_employees,
            }
        )

    header = [
        "date",
        "cases.confirmed.todate",
        "cases.active",
        "quarantine.confirmed.todate",
        "quarantine.active",
        "cases.attendees.confirmed.todate",
        "cases.attendees.active",
        "cases.employees.confirmed.todate",
        "cases.employees.active",
    ]

    with open(outfile, "w", encoding="utf-8") as f:
        csvwriter = csv.DictWriter(
            f, fieldnames=header, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        csvwriter.writeheader()
        csvwriter.writerows(rows)


if __name__ == "__main__":
    school_cases_csv("csv/schools-cases.csv")
