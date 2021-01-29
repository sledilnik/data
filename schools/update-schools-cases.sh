#!/bin/bash

# Podatki Ministrstva za Izobraževanje Znanost in Šport (MIZŠ) RS
# API docs at http://api.mizs.si/api_dokumentacija.html
# jq docs: https://stedolan.github.io/jq/
curl -s https://raw.githubusercontent.com/GK-MIZS/covid/main/api.json | jq '.' \
    | tee schools/schools-cases.json \
    | jq -r 'del( .[0] ) | 
            [   "date",

                "kindergarten.pupils.confirmed",
                "elementary.pupils.confirmed",
                "elementary_special.pupils.confirmed",
                "music.pupils.confirmed",
                "highscool.pupils.confirmed",
                "dormitory.pupils.confirmed",
                "institutions.pupils.confirmed",

                "kindergarten.employees.confirmed",
                "elementary.employees.confirmed",
                "elementary_special.employees.confirmed",
                "music.employees.confirmed",
                "highscool.employees.confirmed",
                "dormitory.employees.confirmed",
                "institutions.employees.confirmed",

                "kindergarten.units.to_quarantine",
                "elementary.units.to_quarantine",
                "elementary_special.units.to_quarantine",
                "music.units.to_quarantine",
                "highscool.units.to_quarantine",
                "dormitory.units.to_quarantine",
                "institutions.units.to_quarantine",

                "kindergarten.pupils.to_quarantine",
                "elementary.pupils.to_quarantine",
                "elementary_special.pupils.to_quarantine",
                "music.pupils.to_quarantine",
                "highscool.pupils.to_quarantine",
                "dormitory.pupils.to_quarantine",
                "institutions.pupils.to_quarantine",

                "kindergarten.pupils.active",
                "elementary.pupils.active",
                "elementary_special.pupils.active",
                "music.pupils.active",
                "highscool.pupils.active",
                "dormitory.pupils.active",
                "institutions.pupils.active",

                "kindergarten.employees.active",
                "elementary.employees.active",
                "elementary_special.employees.active",
                "music.employees.active",
                "highscool.employees.active",
                "dormitory.employees.active",
                "institutions.employees.active",

                "kindergarten.units.quaranteened",
                "elementary.units.quaranteened",
                "elementary_special.units.quaranteened",
                "music.units.quaranteened",
                "highscool.units.quaranteened",
                "dormitory.units.quaranteened",
                "institutions.units.quaranteened",

                "kindergarten.pupils.quaranteened",
                "elementary.pupils.quaranteened",
                "elementary_special.pupils.quaranteened",
                "music.pupils.quaranteened",
                "highscool.pupils.quaranteened",
                "dormitory.pupils.quaranteened",
                "institutions.pupils.quaranteened",

                "kindergarten.units.remote",
                "elementary.units.remote",
                "elementary_special.units.remote",
                "music.units.remote",
                "highscool.units.remote",
                "dormitory.units.remote",
                "institutions.units.remote"
            ],
            (to_entries[] |
            [
                .value.year + "-" + .value.month + "-" + .value.day,

                .value.ucenci_okuzbe_nove.Vrtec,
                .value.ucenci_okuzbe_nove.Osnovna_sola,
                .value.ucenci_okuzbe_nove.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_okuzbe_nove.Glasbena_sola,
                .value.ucenci_okuzbe_nove.Srednja_sola,
                .value.ucenci_okuzbe_nove.Dijaski_dom,
                .value.ucenci_okuzbe_nove.Zavodi,

                .value.zaposleni_okuzbe_nove.Vrtec,
                .value.zaposleni_okuzbe_nove.Osnovna_sola,
                .value.zaposleni_okuzbe_nove.Osnovna_sola_s_prilagojenim_programom,
                .value.zaposleni_okuzbe_nove.Glasbena_sola,
                .value.zaposleni_okuzbe_nove.Srednja_sola,
                .value.zaposleni_okuzbe_nove.Dijaski_dom,
                .value.zaposleni_okuzbe_nove.Zavodi,

                .value.oddelki_v_karanteni_novi.Vrtec,
                .value.oddelki_v_karanteni_novi.Osnovna_sola,
                .value.oddelki_v_karanteni_novi.Osnovna_sola_s_prilagojenim_programom,
                .value.oddelki_v_karanteni_novi.Glasbena_sola,
                .value.oddelki_v_karanteni_novi.Srednja_sola,
                .value.oddelki_v_karanteni_novi.Dijaski_dom,
                .value.oddelki_v_karanteni_novi.Zavodi,

                .value.ucenci_v_karanteni_novi.Vrtec,
                .value.ucenci_v_karanteni_novi.Osnovna_sola,
                .value.ucenci_v_karanteni_novi.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_v_karanteni_novi.Glasbena_sola,
                .value.ucenci_v_karanteni_novi.Srednja_sola,
                .value.ucenci_v_karanteni_novi.Dijaski_dom,
                .value.ucenci_v_karanteni_novi.Zavodi,

                .value.ucenci_okuzbe_aktivne.Vrtec,
                .value.ucenci_okuzbe_aktivne.Osnovna_sola,
                .value.ucenci_okuzbe_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_okuzbe_aktivne.Glasbena_sola,
                .value.ucenci_okuzbe_aktivne.Srednja_sola,
                .value.ucenci_okuzbe_aktivne.Dijaski_dom,
                .value.ucenci_okuzbe_aktivne.Zavodi,

                .value.zaposleni_okuzbe_aktivne.Vrtec,
                .value.zaposleni_okuzbe_aktivne.Osnovna_sola,
                .value.zaposleni_okuzbe_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.zaposleni_okuzbe_aktivne.Glasbena_sola,
                .value.zaposleni_okuzbe_aktivne.Srednja_sola,
                .value.zaposleni_okuzbe_aktivne.Dijaski_dom,
                .value.zaposleni_okuzbe_aktivne.Zavodi,

                .value.oddelki_v_karanteni_aktivne.Vrtec,
                .value.oddelki_v_karanteni_aktivne.Osnovna_sola,
                .value.oddelki_v_karanteni_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.oddelki_v_karanteni_aktivne.Glasbena_sola,
                .value.oddelki_v_karanteni_aktivne.Srednja_sola,
                .value.oddelki_v_karanteni_aktivne.Dijaski_dom,
                .value.oddelki_v_karanteni_aktivne.Zavodi,

                .value.ucenci_v_karanteni_aktivne.Vrtec,
                .value.ucenci_v_karanteni_aktivne.Osnovna_sola,
                .value.ucenci_v_karanteni_aktivne.Osnovna_sola_s_prilagojenim_programom,
                .value.ucenci_v_karanteni_aktivne.Glasbena_sola,
                .value.ucenci_v_karanteni_aktivne.Srednja_sola,
                .value.ucenci_v_karanteni_aktivne.Dijaski_dom,
                .value.ucenci_v_karanteni_aktivne.Zavodi,

                .value.zavodi_pouk_na_daljavo.Vrtec,
                .value.zavodi_pouk_na_daljavo.Osnovna_sola,
                .value.zavodi_pouk_na_daljavo.Osnovna_sola_s_prilagojenim_programom,
                .value.zavodi_pouk_na_daljavo.Glasbena_sola,
                .value.zavodi_pouk_na_daljavo.Srednja_sola,
                .value.zavodi_pouk_na_daljavo.Dijaski_dom,
                .value.zavodi_pouk_na_daljavo.Zavodi

            ]) | @csv' \
    > csv/schools-cases.csv


