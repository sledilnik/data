#!/bin/bash
set -e

csvfilename="merged.csv"
hashbefore=$(sha256sum "$csvfilename")

# collect all dates
OPSI_DATES=$(cat podatki.gov.si/iosprenosi.csv podatki.gov.si/prenosiandroid.csv podatki.gov.si/tanstatistika.csv podatki.gov.si/tanvneseno.csv | cut -d, -f1 | grep "\." | sed -E 's/([0-9]+)\.([0-9]+)\.([0-9]+)/\3-\2-\1/g' | sort | uniq)

# write CSV header
echo "Date,downloads.Android,downloads.Android.todate,downloads.iOS,downloads.iOS.todate,downloads.todate,TAN.issued,TAN.issued.todate,TAN.users,TAN.users.todate,TAN.SIusers,TAN.SIusers.todate" > $csvfilename

todateDLandroid=0
todateDLios=0
todateDL=0
todateTanIssued=0
todateTanUsers=0
for DAY in ${OPSI_DATES};
do 
    SLODATE=$(echo "${DAY}" | sed -E 's/([0-9]+)-([0-9]+)-([0-9]+)/\3.\2.\1/g')

    echo -n "Processing ${DAY} (${SLODATE}):	";

    # Get data from other CSVs
    AndroidDL=$(grep -F "${SLODATE}" podatki.gov.si/prenosiandroid.csv | cut -d, -f2 | sed 's/[^0-9]//g')
    todateDLandroid=$((todateDLandroid + AndroidDL))
    todateDL=$((todateDL + AndroidDL))
    iOSDL=$(grep -F "${SLODATE}" podatki.gov.si/iosprenosi.csv | cut -d, -f2 | sed 's/[^0-9]//g')
    todateDLios=$((todateDLios + iOSDL))
    todateDL=$((todateDL + iOSDL))

    TANsIssued=$(grep -F "${SLODATE}" podatki.gov.si/tanstatistika.csv | cut -d, -f2 | sed 's/[^0-9]//g')
    todateTanIssued=$((todateTanIssued + TANsIssued))

    # Get data from JSON
    TANusers=$(jq -r ".[] | select(.date==\"${DAY}\") | .users_published" "ctt/data.json")
    todateTanUsers=$((todateTanUsers + TANusers))

    TANSIUsers=$(grep -F "${SLODATE}" podatki.gov.si/tanvneseno.csv | cut -d, -f2 | sed 's/[^0-9]//g')
    todateTanSIUsers=$((todateTanSIUsers + TANSIUsers))

    # Write the CSV line (no escaping needed for dates and numbers)
    echo "${DAY},${AndroidDL},${todateDLandroid},${iOSDL},${todateDLios},${todateDL},${TANsIssued},${todateTanIssued},${TANusers},${todateTanUsers},${TANSIUsers},${todateTanSIUsers}" | tee -a $csvfilename
done

hashafter=$(sha256sum "$csvfilename")
if [ "$hashbefore" != "$hashafter" ] ; then
    date +%s > "$csvfilename.timestamp"
fi
