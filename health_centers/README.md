## Pre-requisites:
___
**You need to have a local copy of `COVID-DATA` which is the data folder located in Google Drive of Sledilnik.**
You can either:
* download a folder every time that fresh data needs to be processed
...or
* install Google Drive Backup and Sync desktop app (https://www.google.com/drive/download/) that takes care of automatic sync

If you decide to go with Backup and Sync app you need to take these steps to enable download and automatic sync `COVID-DATA`:
1. Go to `Shared with me` folder
2. Select `COVID-DATA` and press `Shift + Z` to create a hard link in your own namespace
3. Select the destination of `COVID-DATA` under your own namespace
4. Now `COVID-DATA` will show in the list of folders that are available for syncing to your own machine


## How to update health_centers.csv
___
In this folder run:
1. `python3.7 -m venv venv` or `virtualenv -p python3 venv`
1. `source venv/bin/activate`
1. `pip install -r ../requirements.txt`
1. `export COVID_DATA_PATH=<the location of the COVID-DATA folder>`
1. `python process.py`


## CSV field meaning
___
| CSV field | Meaning (EN) | Meaning (SI, original meaning) |
|-|-|-|
| examinations.medical_emergency | No. emergency medical examinations | Št. pregledov NMP |
| examinations.suspected_covid | No. examinations of suspected COVID | Št. pregledov  suma na COVID |
| phone_triage.suspected_covid | No. suspected COVID without examination (telephone triage) | Št. sumov na COVID brez pregleda (triaža po telefonu) |
| tests.performed | No. COVID tests performed | Št. opravljenih testiranj COVID |
| tests.positive | No. positive COVID | Št. pozitivnih COVID |
| sent_to.hospital | No. sent to hospital | Št. napotitev v bolnišnico |
| sent_to.self_isolation | No. sent into self-isolation | Št. napotitev v samoosamitev |
