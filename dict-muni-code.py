#!/usr/bin/env python

import csv
import pandas as pd
df1=pd.read_csv("csv/dict-municipality.csv", index_col='id') [[ "name","iso_code","population" ]]
df1.to_csv("csv/dict-municipality-code.csv", quoting=csv.QUOTE_NONNUMERIC, index_label='id')
