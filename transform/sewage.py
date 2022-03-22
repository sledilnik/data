#!/usr/bin/env python

import os
import tempfile
import typing

import pandas as pd
import requests

from utils import sha1sum, write_timestamp_file


CSV_FOLDER = os.path.join(os.path.dirname(__file__), '../csv')


# https://docs.google.com/spreadsheets/d/14L8wBpkHQij8LKu6TH5BEimPYpnlMDIM
r = requests.get('https://drive.google.com/uc?export=download&id=14L8wBpkHQij8LKu6TH5BEimPYpnlMDIM')
r.raise_for_status()
with tempfile.NamedTemporaryFile() as tf:
    with open(tf.name, 'wb') as f:
        f.write(r.content)
    df = pd.read_excel(io=tf, sheet_name='DATA', engine='openpyxl', parse_dates=['Date']) \
        .rename(columns={'Date': 'date'}) \
        .dropna(subset=['date']) \
        .set_index('date') \
        .drop(columns='NIB Measurements') \
        .dropna(thresh=2)

mapping_dict = {}

def get_location_key(components: typing.List[str]):
    for key in ['kranj', 'ljubljana', 'domzale', 'saleske', 'koper', 'celje', 'maribor']:
        if key in components:
            return key
    raise Exception('No location key found: ', components)

mapping = {}
for column in df.columns:
    if column == 'NIB Measurements':
        mapping['NIB Measurements'] = 'measurements.nib'
        continue

    components = column.lower().split('_')
    location = get_location_key(components=components)
    components.remove(location)
    location = {'saleske': 'velenje'}.get(location, location)  # transform some of the location names
    mapping[column] = f'sewage.{location}.{"-".join(components)}'

df.rename(mapper=mapping, axis='columns', inplace=True)

# export to csv
filename = os.path.join(CSV_FOLDER, 'sewage.csv')
old_hash = sha1sum(filename)
df.to_csv(filename)
write_timestamp_file(filename=filename, old_hash=old_hash)
