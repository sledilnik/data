#!/bin/bash

# Podatki Ministrstva za Izobraževanje Znanost in Šport (MIZŠ) RS
# API docs at http://api.mizs.si/api_dokumentacija.html
# jq docs: https://stedolan.github.io/jq/
curl -s http://api.mizs.si/stats/ | jq '.' \
    | tee json/mizs-stats.json \
    | jq -r 'del( .[0] ) | to_entries[] |
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

            ] | @csv' \
    > csv/mizs-stats.csv
