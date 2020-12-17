import copy
import csv
import glob
import os
import time
from datetime import datetime, timedelta

import pandas as pd


covid_data_path = os.getenv('COVID_DATA_PATH')
assert covid_data_path, 'COVID_DATA_PATH env variable must be set. (The location of the COVID-DATA folder)'
SOURCE_FILE = max(glob.glob(os.path.join(covid_data_path, 'EPI') + '/dnevni_prikazi*.xlsx'))  # take latest
CSV_FOLDER = os.path.join(os.path.dirname(__file__), '../csv')

municipalities = {}
with open(os.path.join(CSV_FOLDER, 'dict-municipality.csv')) as f:
    for row in csv.DictReader(f):
        municipalities[row['name'].lower()] = row
        if row['name_alt']:
            municipalities[row['name_alt'].lower()] = row

def get_municipality_header(municipality: str):
    """ Transforms municipality name from NIJZ xlsx to the municipality header used in final CSVs.
        For instance: Sveti Andraž v Slov.goricah --> region.mb.sveti_andraž_v_slovenskih_goricah
    """
    if municipality == 'NEZNANO':
        return 'region.n.neznano'
    if municipality == 'TUJINA':
        return 'region.t.tujina'
    m = municipality.lower()
    if m == 'sveti andraž v slov.goricah':  # handle typo in xlsx
        m = 'sveti andraž v slov. goricah'
    region = municipalities[m]['region']
    id_ = municipalities[m]['id']
    return f'region.{region}.{id_}'

df = pd.read_excel(io=SOURCE_FILE, sheet_name='Tabela 2', engine='openpyxl', skiprows=[0, 2], skipfooter=1).transpose()[:-1]
df.columns = df.iloc[0]  # sets the header to municipality name instead of having a zero-based index for header
df = df[1:]  # now that municipality is set for the header, we can delete it from the value matrix

df.index.rename('date', inplace=True)  # rename the index since what's contained there are actual dates
df = df.rename(mapper=get_municipality_header, axis='columns')  # transform of municipality names
df = df.rename(mapper=lambda x: datetime.strptime(x, '%d.%m.%Y'), axis='rows')  # transforms strings to datetime
df = df.reindex(sorted(df.columns), axis=1)  # sorts the columns

df.cumsum().replace({0: None}).astype('Int64') \
    .to_csv(os.path.join(CSV_FOLDER, 'regions.csv'), line_terminator='\r\n')

df.rolling(min_periods=1, window=14).sum().replace({0: None}).astype('Int64') \
    .drop('region.n.neznano', axis='columns') \
    .to_csv(os.path.join(CSV_FOLDER, 'active-regions.csv'), line_terminator='\r\n')

with open(os.path.join(CSV_FOLDER, 'dict-municipality.csv')) as f:
    for row in csv.DictReader(f):
        municipalities[row['name'].lower()] = row
        if row['name_alt']:
            municipalities[row['name_alt'].lower()] = row

# --- deceased-regions.csv ---
# Copy paste latest row for every missing date
with open(os.path.join(CSV_FOLDER, 'deceased-regions.csv')) as f:
    rows = [row for row in csv.DictReader(f)]
while (latest_date := datetime.strptime(rows[-1]['date'], '%Y-%m-%d').date()) < datetime.now().date():
    rows.append(copy.deepcopy(rows[-1]))
    rows[-1]['date'] = str(latest_date + timedelta(days=1))
# Write the rows collection back to the csv
with open(os.path.join(CSV_FOLDER, 'deceased-regions.csv'), 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# --- timestamped files ---
timestamp = int(time.time())
for f in ('regions.csv.timestamp', 'active-regions.csv.timestamp', 'deceased-regions.csv.timestamp'):
    with open(os.path.join(CSV_FOLDER, f), 'w', newline='') as csvfile:
        csvfile.write(f'{timestamp}\n')
