#!/bin/bash

# Podatki Ministrstva za Izobraževanje Znanost in Šport (MIZŠ) RS
# API docs at http://api.mizs.si/api_dokumentacija.html
# jq docs: https://stedolan.github.io/jq/
curl -s https://api.mizs.si/stats/ | jq '.' \
    | tee json/mizs-stats.json \
    | jq -r 'del( .[0] ) | 
            [   "date",

                "pupils_infected_new.kindergarten",
                "pupils_infected_new.elementary",
                "pupils_infected_new.elementary_special",
                "pupils_infected_new.music",
                "pupils_infected_new.highscool",
                "pupils_infected_new.dormitory",
                "pupils_infected_new.institutions",

                "employees_infected_new.kindergarten",
                "employees_infected_new.elementary",
                "employees_infected_new.elementary_special",
                "employees_infected_new.music",
                "employees_infected_new.highscool",
                "employees_infected_new.dormitory",
                "employees_infected_new.institutions",

                "units_quaranteened_new.kindergarten",
                "units_quaranteened_new.elementary",
                "units_quaranteened_new.elementary_special",
                "units_quaranteened_new.music",
                "units_quaranteened_new.highscool",
                "units_quaranteened_new.dormitory",
                "units_quaranteened_new.institutions",

                "pupils_quaranteened_new.kindergarten",
                "pupils_quaranteened_new.elementary",
                "pupils_quaranteened_new.elementary_special",
                "pupils_quaranteened_new.music",
                "pupils_quaranteened_new.highscool",
                "pupils_quaranteened_new.dormitory",
                "pupils_quaranteened_new.institutions",

                "pupils_infected.kindergarten",
                "pupils_infected.elementary",
                "pupils_infected.elementary_special",
                "pupils_infected.music",
                "pupils_infected.highscool",
                "pupils_infected.dormitory",
                "pupils_infected.institutions",

                "employees_infected.kindergarten",
                "employees_infected.elementary",
                "employees_infected.elementary_special",
                "employees_infected.music",
                "employees_infected.highscool",
                "employees_infected.dormitory",
                "employees_infected.institutions",

                "units_quaranteened.kindergarten",
                "units_quaranteened.elementary",
                "units_quaranteened.elementary_special",
                "units_quaranteened.music",
                "units_quaranteened.highscool",
                "units_quaranteened.dormitory",
                "units_quaranteened.institutions",

                "pupils_quaranteened.kindergarten",
                "pupils_quaranteened.elementary",
                "pupils_quaranteened.elementary_special",
                "pupils_quaranteened.music",
                "pupils_quaranteened.highscool",
                "pupils_quaranteened.dormitory",
                "pupils_quaranteened.institutions",

                "teaching_remote.kindergarten",
                "teaching_remote.elementary",
                "teaching_remote.elementary_special",
                "teaching_remote.music",
                "teaching_remote.highscool",
                "teaching_remote.dormitory",
                "teaching_remote.institutions"
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
    > csv/mizs-stats.csv


