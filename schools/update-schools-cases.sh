#!/bin/bash
set -e

# Podatki Ministrstva za Izobraževanje Znanost in Šport (MIZŠ) RS
# API docs at http://api.mizs.si/api_dokumentacija.html
# jq docs: https://stedolan.github.io/jq/
csvfilename="csv/schools-cases.csv"
hashbefore=$(sha256sum "$csvfilename")

# Alternative source: https://raw.githubusercontent.com/GK-MIZS/covid/main/api.json
curl -s https://podatki.gov.si/dataset/92670859-fae3-4225-adf4-17be511b87d3/resource/bfde646f-3b36-4003-b4b2-bcdba3932cde/download/api.json | jq '.' \
    | tee schools/schools-cases.json \
    | jq -r 'del( .[0] ) | 
            [   "date",

                "kindergarten.employees.confirmed",
                "kindergarten.employees.active",
                "kindergarten.attendees.confirmed",
                "kindergarten.attendees.active",
                "kindergarten.attendees.to_quarantine",
                "kindergarten.attendees.quarantined",
                "kindergarten.units.to_quarantine",
                "kindergarten.units.quarantined",
                "kindergarten.units.remote",

                "elementary.employees.confirmed",
                "elementary.employees.active",
                "elementary.attendees.confirmed",
                "elementary.attendees.active",
                "elementary.attendees.to_quarantine",
                "elementary.attendees.quarantined",
                "elementary.units.to_quarantine",
                "elementary.units.quarantined",
                "elementary.units.remote",

                "elementary_special.employees.confirmed",
                "elementary_special.employees.active",
                "elementary_special.attendees.confirmed",
                "elementary_special.attendees.active",
                "elementary_special.attendees.to_quarantine",
                "elementary_special.attendees.quarantined",
                "elementary_special.units.to_quarantine",
                "elementary_special.units.quarantined",
                "elementary_special.units.remote",

                "music.employees.confirmed",
                "music.employees.active",
                "music.attendees.confirmed",
                "music.attendees.active",
                "music.attendees.to_quarantine",
                "music.attendees.quarantined",
                "music.units.to_quarantine",
                "music.units.quarantined",
                "music.units.remote",

                "highschool.employees.confirmed",
                "highschool.employees.active",
                "highschool.attendees.confirmed",
                "highschool.attendees.active",
                "highschool.attendees.to_quarantine",
                "highschool.attendees.quarantined",
                "highschool.units.to_quarantine",
                "highschool.units.quarantined",
                "highschool.units.remote",

                "dormitory.employees.confirmed",
                "dormitory.employees.active",
                "dormitory.attendees.confirmed",
                "dormitory.attendees.active",
                "dormitory.attendees.to_quarantine",
                "dormitory.attendees.quarantined",
                "dormitory.units.to_quarantine",
                "dormitory.units.quarantined",
                "dormitory.units.remote",

                "institutions.employees.confirmed",
                "institutions.employees.active",
                "institutions.attendees.confirmed",
                "institutions.attendees.active",
                "institutions.attendees.to_quarantine",
                "institutions.attendees.quarantined",
                "institutions.units.to_quarantine",
                "institutions.units.quarantined",
                "institutions.units.remote"
            ],
            (to_entries[] |
            [
                .value.year + "-" + .value.month + "-" + .value.day,

                .value.zaposleni_okuzbe_nove.Vrtec,
                .value.zaposleni_okuzbe_aktivne.Vrtec,
                .value.ucenci_okuzbe_nove.Vrtec,
                .value.ucenci_okuzbe_aktivne.Vrtec,
                .value.ucenci_v_karanteni_novi.Vrtec,
                .value.ucenci_v_karanteni_aktivne.Vrtec,
                .value.oddelki_v_karanteni_novi.Vrtec,
                .value.oddelki_v_karanteni_aktivne.Vrtec,
                .value.zavodi_pouk_na_daljavo.Vrtec,

                .value.zaposleni_okuzbe_nove.Osnovna_sola,
                .value.zaposleni_okuzbe_aktivne.Osnovna_sola,
                .value.ucenci_okuzbe_nove.Osnovna_sola,
                .value.ucenci_okuzbe_aktivne.Osnovna_sola,
                .value.ucenci_v_karanteni_novi.Osnovna_sola,
                .value.ucenci_v_karanteni_aktivne.Osnovna_sola,
                .value.oddelki_v_karanteni_novi.Osnovna_sola,
                .value.oddelki_v_karanteni_aktivne.Osnovna_sola,
                .value.zavodi_pouk_na_daljavo.Osnovna_sola,

                .value.zaposleni_okuzbe_nove.Osnovna_sola_s_prilagojenim_programom,
                .value.zaposleni_okuzbe_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_okuzbe_nove.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_okuzbe_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_v_karanteni_novi.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_v_karanteni_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.oddelki_v_karanteni_novi.Osnovna_sola_s_prilagojenim_programom,
                .value.oddelki_v_karanteni_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.zavodi_pouk_na_daljavo.Osnovna_sola_s_prilagojenim_programom,

                .value.zaposleni_okuzbe_nove.Glasbena_sola,
                .value.zaposleni_okuzbe_aktivne.Glasbena_sola,
                .value.ucenci_okuzbe_nove.Glasbena_sola,
                .value.ucenci_okuzbe_aktivne.Glasbena_sola,
                .value.ucenci_v_karanteni_novi.Glasbena_sola,
                .value.ucenci_v_karanteni_aktivne.Glasbena_sola,
                .value.oddelki_v_karanteni_novi.Glasbena_sola,
                .value.oddelki_v_karanteni_aktivne.Glasbena_sola,
                .value.zavodi_pouk_na_daljavo.Glasbena_sola,

                .value.zaposleni_okuzbe_nove.Srednja_sola,
                .value.zaposleni_okuzbe_aktivne.Srednja_sola,
                .value.ucenci_okuzbe_nove.Srednja_sola,
                .value.ucenci_okuzbe_aktivne.Srednja_sola,
                .value.ucenci_v_karanteni_novi.Srednja_sola,
                .value.ucenci_v_karanteni_aktivne.Srednja_sola,
                .value.oddelki_v_karanteni_novi.Srednja_sola,
                .value.oddelki_v_karanteni_aktivne.Srednja_sola,
                .value.zavodi_pouk_na_daljavo.Srednja_sola,

                .value.zaposleni_okuzbe_nove.Dijaski_dom,
                .value.zaposleni_okuzbe_aktivne.Dijaski_dom,
                .value.ucenci_okuzbe_nove.Dijaski_dom,
                .value.ucenci_okuzbe_aktivne.Dijaski_dom,
                .value.ucenci_v_karanteni_novi.Dijaski_dom,
                .value.ucenci_v_karanteni_aktivne.Dijaski_dom,
                .value.oddelki_v_karanteni_novi.Dijaski_dom,
                .value.oddelki_v_karanteni_aktivne.Dijaski_dom,
                .value.zavodi_pouk_na_daljavo.Dijaski_dom,

                .value.zaposleni_okuzbe_nove.Zavodi,
                .value.zaposleni_okuzbe_aktivne.Zavodi,
                .value.ucenci_okuzbe_nove.Zavodi,
                .value.ucenci_okuzbe_aktivne.Zavodi,
                .value.ucenci_v_karanteni_novi.Zavodi,
                .value.ucenci_v_karanteni_aktivne.Zavodi,
                .value.oddelki_v_karanteni_novi.Zavodi,
                .value.oddelki_v_karanteni_aktivne.Zavodi,
                .value.zavodi_pouk_na_daljavo.Zavodi

            ]) | @csv' \
    > $csvfilename

hashafter=$(sha256sum "$csvfilename")
if [ "$hashbefore" != "$hashafter" ] ; then
    date +%s > "$csvfilename.timestamp"
fi
