#!/usr/bin/env python

import pandas as pd


df = pd.read_csv('csv/dict-schools.csv', index_col='zavid')

df = df.reindex(['matzavid', 'type', 'region', 'name'], axis='columns')

df.to_csv("schools.csv", float_format='%.0f', quoting=1)

