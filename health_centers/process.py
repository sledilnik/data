#!/usr/bin/env python
import argparse
import collections
import csv
import datetime
import locale
import os
import re

import openpyxl

import dataclass
import mappings


# in order to sort č, š, ž right (also use key=locale.strxfrm when sorting by string)
locale.setlocale(locale.LC_ALL, 'sl_SI.utf8')

def check_directory(value):
    dir_abs_path = os.path.abspath(value)
    if not os.path.exists(dir_abs_path):
        raise argparse.ArgumentTypeError(f'Directory {dir_abs_path} does not exist')
    return dir_abs_path

parser = argparse.ArgumentParser(description='Procesiraj stanje zalog v ZD')
parser.add_argument('-d', '--dir', help='Direktorij za procesiranje', required=True, type=check_directory)
parser.add_argument('-f', '--file', help='Output file', required=True)

args = parser.parse_args()
dir_abs_path = args.dir
list_dir = [os.path.join(dir_abs_path, x) for x in os.listdir(dir_abs_path)]
files = [x for x in list_dir if os.path.isfile(x)]

# dir contents validation
assert not [x for x in list_dir if os.path.isdir(x)], f'Directory {dir_abs_path} should contain only files, no folders'
assert all(f.endswith('.xlsx') for f in files), 'All files should end with .xlsx'

sheets = [openpyxl.load_workbook(f).active for f in files]
# file content validation
for sheet in sheets:
    expected = [  # header row 1
        'Št.', 'ZD', 'Datum', 'Št. pregledov NMP', 'Št. pregledov  suma na COVID',
        r'Št. sumov na COVID brez pregleda \(triaža po telefonu\)', 'Št. opravljenih testiranj COVID',
        'Št.  pozitivnih COVID', 'Št. napotitev v bolnišnico', 'Št. napotitev v samoosamitev', 'Opombe'
    ]
    actual = [cell.value for cell in sheet[1]]
    for expected_col, actual_col in zip(expected, actual):
        assert re.match(expected_col, actual_col), (sheet, expected_col, actual_col)

# process
entities = []
for sheet in sheets:
    for row in list(sheet.iter_rows())[2:]:  # skip header rows
        if row[0].value is None and row[1].value == 'SKUPAJ':
            break  # aggregates do not interest us, also do not continue since all the relevant data is extracted
        # make sure the name is always there
        assert row[1].value is not None, sheet
        # make sure the date is always there
        if row[2].value is None:  # some cells are missing dates
            search = re.search(r'<Worksheet "(\d{1,2})\.(\d{1,2})\.">', str(sheet))
            assert datetime.datetime.now().year == 2020  # this extraction logic could be broken in 2021
            date = datetime.datetime(year=2020, month=int(search.group(2)), day=int(search.group(1))).date()
        else:
            date = row[2].value.date()
        entities.append(dataclass.Entity(
            name=row[1].value,
            date=date,
            numbers=dataclass.Numbers(
                examinations___medical_emergency=row[3].value,  # Št. pregledov NMP
                examinations___suspected_covid=row[4].value,  # Št. pregledov  suma na COVID
                phone_triage___suspected_covid=row[5].value,  # Št. sumov na COVID brez pregleda (triaža po telefonu)
                tests___performed=row[6].value,  # Št. opravljenih testiranj COVID
                tests___positive=row[7].value,  # Št.  pozitivnih COVID
                sent_to___hospital=row[8].value,  # Št. napotitev v bolnišnico
                sent_to___self_isolation=row[9].value  # Št. napotitev v samoosamitev
            )
        ))
# sort so that we'll only iterate once when writing to csv
entities.sort(key=lambda entity: locale.strxfrm(entity.name_key), reverse=True)
entities.sort(key=lambda entity: entity.date, reverse=True)

aggregates = collections.defaultdict(lambda: dataclass.Numbers(0, 0, 0, 0, 0, 0, 0))
for entity in entities:
    for key in dataclass.Numbers.__annotations__.keys():
        aggregates[entity.date].__dict__[key] += entity.numbers.__dict__[key] or 0  # handle Null


with open(args.file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, dialect='excel')

    def get_formatted_numbers_fields():
        return[field.replace('___', '.') for field in dataclass.Numbers.__annotations__.keys()]

    columns = ['date']
    # scope: aggregates
    for field in get_formatted_numbers_fields():
        columns.append(f'hc.{field}')
    # scope: health centers
    for name in mappings.unique_short_names:
        region = mappings.region[name]
        for field in get_formatted_numbers_fields():
            columns.append(f'hc.{region}.{name}.{field}')
    writer.writerow(columns)

    # write data
    dates = sorted(list(set([entity.date for entity in entities])))
    for date in dates:

        columns = [date]
        # scope: aggregates
        for key in aggregates[date].__annotations__.keys():
            columns.append(aggregates[date].__dict__[key])
        # scope: health centers
        for name in mappings.unique_short_names:
            entity = entities.pop()
            assert entity.name_key == name and entity.date == date
            for field in dataclass.Numbers.__annotations__.keys():
                columns.append(getattr(entity.numbers, field))
        writer.writerow(columns)
