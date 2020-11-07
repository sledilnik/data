#!/bin/bash

mkdir -p ctt || true
curl -s https://ostanizdrav.sledilnik.org/plots/data.json         | jq '.' > ctt/data.json
curl -s https://ostanizdrav.sledilnik.org/plots/dataByRisk.json   | jq '.' > ctt/dataByRisk.json
curl -s https://ostanizdrav.sledilnik.org/plots/usersByCount.json | jq '.' > ctt/usersByCount.json
 
# mkdir -p gov.si || true
# curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/element/83674/izvoz.csv -o gov.si/app-downloads.csv
# curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/element/83668/izvoz.csv -o gov.si/tan-issued.csv

# https://podatki.gov.si/dataset/statisticni-podatki-aplikacije-ostanizdrav
mkdir -p podatki.gov.si || true
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/f8711982-df42-48e6-9c07-92fcb89cb15c/download/prenosiandroid.csv -o podatki.gov.si/prenosiandroid.csv
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/cf4601a8-edb0-4c3e-8646-a8d9a4094375/download/iosprenosi.csv -o podatki.gov.si/iosprenosi.csv
curl --insecure https://podatki.gov.si/dataset/d3e718b3-01f0-40bd-93b0-b56d3bb4e97f/resource/406b4306-cf45-4d49-b44e-48c8b4c1de78/download/tanstatistika.csv -o podatki.gov.si/tanstatistika.csv

./merge.sh
