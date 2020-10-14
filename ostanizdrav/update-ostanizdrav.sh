#!/bin/bash

mkdir -p ctt || true
curl -s https://ostanizdrav.sledilnik.org/plots/data.json         | jq '.' > ctt/data.json
curl -s https://ostanizdrav.sledilnik.org/plots/dataByRisk.json   | jq '.' > ctt/dataByRisk.json
curl -s https://ostanizdrav.sledilnik.org/plots/usersByCount.json | jq '.' > ctt/usersByCount.json
 
mkdir -p gov.si || true
curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/element/83674/izvoz.csv -o gov.si/app-downloads.csv
curl https://www.gov.si/teme/koronavirus-sars-cov-2/mobilna-aplikacija-ostanizdrav/element/83668/izvoz.csv -o gov.si/tan-issued.csv

