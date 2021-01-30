#!/bin/bash

# Podatki Ministrstva za Izobraževanje Znanost in Šport (MIZŠ) RS
# API docs at http://api.mizs.si/api_dokumentacija.html
# jq docs: https://stedolan.github.io/jq/
curl -s https://raw.githubusercontent.com/GK-MIZS/covid/main/api.json | jq '.' \
    | tee schools/schools-cases.json \
    | jq -r 'del( .[0] ) | 
            [   "date",

                "kindergarten.employees.confirmed",
                "kindergarten.employees.active",
                "kindergarten.attendees.confirmed",
                "kindergarten.attendees.active",
                "kindergarten.attendees.to_quarantine",
                "kindergarten.attendees.quaranteened",
                "kindergarten.units.to_quarantine",
                "kindergarten.units.quaranteened",
                "kindergarten.units.remote",

                "elementary.employees.confirmed",
                "elementary.employees.active",
                "elementary.attendees.confirmed",
                "elementary.attendees.active",
                "elementary.attendees.to_quarantine",
                "elementary.attendees.quaranteened",
                "elementary.units.to_quarantine",
                "elementary.units.quaranteened",
                "elementary.units.remote",

                "elementary_special.employees.confirmed",
                "elementary_special.employees.active",
                "elementary_special.attendees.confirmed",
                "elementary_special.attendees.active",
                "elementary_special.attendees.to_quarantine",
                "elementary_special.attendees.quaranteened",
                "elementary_special.units.to_quarantine",
                "elementary_special.units.quaranteened",
                "elementary_special.units.remote",

                "music.employees.confirmed",
                "music.employees.active",
                "music.attendees.confirmed",
                "music.attendees.active",
                "music.attendees.to_quarantine",
                "music.attendees.quaranteened",
                "music.units.to_quarantine",
                "music.units.quaranteened",
                "music.units.remote",

                "highscool.employees.confirmed",
                "highscool.employees.active",
                "highscool.attendees.confirmed",
                "highscool.attendees.active",
                "highscool.attendees.to_quarantine",
                "highscool.attendees.quaranteened",
                "highscool.units.to_quarantine",
                "highscool.units.quaranteened",
                "highscool.units.remote",

                "dormitory.employees.confirmed",
                "dormitory.employees.active",
                "dormitory.attendees.confirmed",
                "dormitory.attendees.active",
                "dormitory.attendees.to_quarantine",
                "dormitory.attendees.quaranteened",
                "dormitory.units.to_quarantine",
                "dormitory.units.quaranteened",
                "dormitory.units.remote",

                "institutions.employees.confirmed",
                "institutions.employees.active",
                "institutions.attendees.confirmed",
                "institutions.attendees.active",
                "institutions.attendees.to_quarantine",
                "institutions.attendees.quaranteened",
                "institutions.units.to_quarantine",
                "institutions.units.quaranteened",
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
    > csv/schools-cases.csv


