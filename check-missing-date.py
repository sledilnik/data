import pandas as pd

df = pd.read_csv('csv/cases.csv', parse_dates=['date'])

date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())

missing_dates = date_range.difference(df['date'])

if missing_dates.empty:
    print("No missing dates.")
else:
    print("Missing dates:")
    print(missing_dates)

