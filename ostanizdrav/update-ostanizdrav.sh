#!/bin/bash
set -e

mkdir -p ctt || true
curl -s https://ostanizdrav.sledilnik.org/plots/data.json         | jq '.' > ctt/data.json
curl -s https://ostanizdrav.sledilnik.org/plots/dataByRisk.json   | jq '.' > ctt/dataByRisk.json
curl -s https://ostanizdrav.sledilnik.org/plots/usersByCount.json | jq '.' > ctt/usersByCount.json
 
mkdir -p gov.si || true
# curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/element/83674/izvoz.csv -o gov.si/app-downloads.csv
# curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/element/83668/izvoz.csv -o gov.si/tan-issued.csv
curl https://www.gov.si/assets/ministrstva/MJU/devices.csv -o gov.si/devices.csv
# curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/statistika/ -o gov.si/statistika.html

# https://podatki.gov.si/dataset/statisticni-podatki-aplikacije-ostanizdrav
mkdir -p podatki.gov.si || true
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/f8711982-df42-48e6-9c07-92fcb89cb15c/download/prenosiandroid.csv -o podatki.gov.si/prenosiandroid.csv
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/1786b9c7-def2-40f0-bccf-7866b5878ef5/download/iosprenosi.csv -o podatki.gov.si/iosprenosi.csv
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/406b4306-cf45-4d49-b44e-48c8b4c1de78/download/tanstatistika.csv -o podatki.gov.si/tanstatistika.csv
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/1167a46b-22ac-455f-b134-fedaf258ea0d/download/tanvneseno.csv -o podatki.gov.si/tanvneseno.csv
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/3710deae-85c9-41e5-ab27-cb06f6f74533/download/agregacijaostanizdrav.json -o podatki.gov.si/agregacijaostanizdrav.json

./fixdates.sh podatki.gov.si/prenosiandroid.csv
./fixdates.sh podatki.gov.si/iosprenosi.csv
./fixdates.sh podatki.gov.si/tanstatistika.csv
./fixdates.sh podatki.gov.si/tanvneseno.csv

./merge.sh
