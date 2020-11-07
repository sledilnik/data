#!/bin/bash

# collect all dates
OPSI_DATES=$(cat podatki.gov.si/iosprenosi.csv podatki.gov.si/prenosiandroid.csv podatki.gov.si/tanstatistika.csv | cut -d, -f1 | grep "\." | sed -E 's/([0-9]+)\.([0-9]+)\.([0-9]+)/\3-\2-\1/g' | sort | uniq)

# write CSV header
echo "Date,Android_downloads,iOS_downloads,TAN_issued,TAN_users" > merged.csv

for DAY in ${OPSI_DATES};
do 
    SLODATE=$(echo "${DAY}" | sed -E 's/([0-9]+)-([0-9]+)-([0-9]+)/\3.\2.\1/g')

    echo -n "Processing ${DAY} (${SLODATE}):	";

    # Get data from other CSVs
    AndroidDL=$(grep -F "${SLODATE}" podatki.gov.si/prenosiandroid.csv | cut -d, -f2 | sed 's/[^0-9]//g')
    iOSDL=$(grep -F "${SLODATE}" podatki.gov.si/iosprenosi.csv | cut -d, -f2 | sed 's/[^0-9]//g')
    TANsIssued=$(grep -F "${SLODATE}" podatki.gov.si/tanstatistika.csv | cut -d, -f2 | sed 's/[^0-9]//g')

    # Get data from JSON
    TANusers=$(jq -r ".[] | select(.date==\"${DAY}\") | .users_published" "ctt/data.json")

    # Write the CSV line (no escaping needed for dates and numbers)
    echo "${DAY},${AndroidDL},${iOSDL},${TANsIssued},${TANusers}" | tee -a merged.csv
done