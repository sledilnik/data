#!/usr/bin/env python
import sys
import pathlib
# get repo root folder and add it to PYTHONPATH (so that we don't need to install this package)
repo_root_path = str(pathlib.Path(__file__).parent.absolute().parent)
if repo_root_path not in sys.path:
    sys.path.append(repo_root_path)

import collections
import csv
import datetime
import glob
import logging
import os
import re
import requests
import tempfile
import time
import typing
import zipfile

import openpyxl

import health_centers.dataclass
import health_centers.mappings


def get_sheet_hos(xlsx_file: str):
    """ We have to fetch appropriate sheet for HOS, since
            * xlsx contains multiple sheets
            * there's no guarantee relevant sheet is actually there
    """
    wb = openpyxl.load_workbook(xlsx_file)
    for sheet_name in ['Bolnišnice COVID točke', 'Bonišnice COVID točke', 'Bolnišnica COVID točke']:
        if sheet_name in wb.sheetnames:
            return wb[sheet_name]
    logging.warning(f'{xlsx_file} has no relevant sheet present')


def list_xlsx(dir: str):
    """ Lists all .xlsx files in a directory recursively.
    """
    return glob.glob(dir + '/**/*.xlsx', recursive=True)


def read_sheets(sheets: typing.List[openpyxl.worksheet.worksheet.Worksheet]):
    logging.info('Standardization: Removing starting column "Št." if present...')
    for sheet in sheets:
        headers = [cell.value for cell in sheet[1]]
        if headers[0] == 'Št.':
            sheet.delete_cols(0)

    logging.info('Validating columns...')
    # file content validation
    for sheet in sheets:
        expected = [  # header row 1
            r'ZD|Bolnišnica|Bolnišnice|SB', 'Datum', 'Št. pregledov NMP', r'Št. pregledov. suma na COVID',
            r'Št. sumov na COVID brez pregleda \(triaža po telefonu\)', 'Št. opravljenih testiranj COVID',
            r'Št\.. pozitivnih COVID', 'Št. napotitev v bolnišnico', 'Št. napotitev v samoosamitev', 'Opombe'
        ]
        actual = [cell.value for cell in sheet[1]]
        for expected_col, actual_col in zip(expected, actual):
            assert re.match(expected_col, actual_col), (sheet.file, sheet, expected_col, actual_col)

    logging.info('Reading sheets and building entity collection...')
    entities = []
    for sheet in sheets:
        for row in list(sheet.iter_rows())[2:]:  # skip header rows
            if row[0].value == 'SKUPAJ' or all([cell.value == '' or cell.value is None for cell in row]):
                break  # aggregates do not interest us, also do not continue since all the relevant data is extracted
            # make sure the name is always there
            assert row[0].value is not None, (sheet.file, sheet)
            # make sure the date is always there
            if row[1].value is None:  # some cells are missing dates
                search = re.search(r'<Worksheet "(\d{1,2})\.(\d{1,2})\.">', str(sheet))
                assert datetime.datetime.now().year == 2020  # this extraction logic could be broken in 2021
                date = datetime.datetime(year=2020, month=int(search.group(2)), day=int(search.group(1))).date()
            else:
                date = row[1].value.date()
            try:
                entity = health_centers.dataclass.Entity(
                    name=row[0].value,
                    # the date we get from xslx means date when data was gathered
                    # the data itself is for the day before that
                    date=date - datetime.timedelta(days=1),
                    sheet=str(sheet),
                    file=sheet.file,
                    numbers=health_centers.dataclass.Numbers(
                        # Št. pregledov NMP
                        examinations___medical_emergency=row[2].value,
                        # Št. pregledov  suma na COVID
                        examinations___suspected_covid=row[3].value,
                        # Št. sumov na COVID brez pregleda (triaža po telefonu)
                        phone_triage___suspected_covid=row[4].value,
                        # Št. opravljenih testiranj COVID
                        tests___performed=row[5].value,
                        # Št.  pozitivnih COVID
                        tests___positive=row[6].value,
                        # Št. napotitev v bolnišnico
                        sent_to___hospital=row[7].value,
                        # Št. napotitev v samoosamitev
                        sent_to___self_isolation=row[8].value
                    )
                )
            except Exception as e:
                raise type(e)(str(e), sheet.file)
            entities.append(entity)
    return entities


def main():
    KOOFR_ROOT = 'https://app.koofr.net/'
    KOOFR_ID_ZD = 'b232782b-9893-4278-b54c-faf461fce4bd'
    KOOFR_ID_HOS = '2c90ec11-f01e-4fb0-86fd-d430c1fff181'
    KOOFR_PASS_ZD = os.getenv('ZD_ZIP_PASS')
    assert KOOFR_PASS_ZD, 'Environmental variable ZD_ZIP_PASS must be set.'
    KOOFR_PASS_HOS = os.getenv('HOS_ZIP_PASS')
    assert KOOFR_PASS_HOS, 'Environmental variable HOS_ZIP_PASS must be set.'

    logging.basicConfig(level=logging.INFO)

    logging.info('Refreshing Koofr cache...')
    for url in [
        f'{KOOFR_ROOT}api/v2/public/links/{KOOFR_ID_ZD}/bundle?path=%2F&password={KOOFR_PASS_ZD}',
        f'{KOOFR_ROOT}api/v2/public/links/{KOOFR_ID_HOS}/bundle?path=%2F&password={KOOFR_PASS_HOS}'
    ]:
        resp = requests.get(url, headers={'User-Agent': 'curl'})
        assert resp.status_code == 200, (url, resp.status_code)
    time.sleep(5)

    def get_archive(tmp_dir: str, folder_id: str, file_id: str, password: str):
        url = f'{KOOFR_ROOT}content/links/{folder_id}/files/get/{file_id}?path=%2F&password={password}'
        logging.info(f'Fetching {url}')
        resp = requests.get(url, headers={'User-Agent': 'curl'})
        zip_path = os.path.join(tmp_dir, 'temp.zip')
        with open(zip_path, 'wb') as f:
            f.write(resp.content)
        logging.info('Extracting archive...')
        zipfile.ZipFile(zip_path).extractall(path=tmp_dir)
        logging.info('List of fetched .xlsx files:')
        files = list_xlsx(dir=tmp_dir)
        for f in files:
            logging.info(f.split('/')[-1])
        return files

    entities = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        files = get_archive(tmp_dir=tmp_dir, folder_id=KOOFR_ID_HOS, file_id='HOS.zip', password=KOOFR_PASS_HOS)
        sheets = []
        for f in files:
            sheet = get_sheet_hos(xlsx_file=f)
            if sheet is not None:
                sheet.file = f
                sheets.append(sheet)
        entities.extend(read_sheets(sheets=sheets))

    with tempfile.TemporaryDirectory() as tmp_dir:
        files = get_archive(tmp_dir=tmp_dir, folder_id=KOOFR_ID_ZD, file_id='ZD.zip', password=KOOFR_PASS_ZD)
        sheets = []
        for f in files:
            sheet = openpyxl.load_workbook(f).active
            sheet.file = f
            sheets.append(sheet)
        entities.extend(read_sheets(sheets=sheets))
    entities.sort(key=lambda entity: entity.name)
    entities.sort(key=lambda entity: entity.date)

    aggregates = collections.defaultdict(lambda: health_centers.dataclass.Numbers(0, 0, 0, 0, 0, 0, 0))
    for entity in entities:
        for key in health_centers.dataclass.Numbers.__annotations__.keys():
            aggregates[entity.date].__dict__[key] += entity.numbers.__dict__[key] or 0  # handle Null

    logging.info('Writing CSV...')
    repo_root_health_centers = os.path.dirname(os.path.abspath(__file__))
    assert repo_root_health_centers.endswith('/data/health_centers')
    repo_root = '/'.join(repo_root_health_centers.split('/')[:-1])
    assert repo_root.endswith('/data')
    health_centers_csv = os.path.join(repo_root, 'csv/health_centers.csv')

    def get_entity(name_key: str, date: datetime):
        found_entities = []
        for entity in entities:
            if entity.name_key == name_key and entity.date == date:
                found_entities.append(entity)
        if len(found_entities) == 0:
            logging.warning(f'No data found for {name_key} {date}')
            return None
        if len(found_entities) > 1:
            for found_entity in found_entities:
                logging.error(found_entity)
            raise Exception(f'Too many entities found: {len(found_entities)}, {name_key}, {date}')
        return found_entities[0]

    with open(health_centers_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')

        def get_formatted_numbers_fields():
            return[field.replace('___', '.') for field in health_centers.dataclass.Numbers.__annotations__.keys()]

        columns = ['date']
        # scope: aggregates
        for field in get_formatted_numbers_fields():
            columns.append(f'hc.{field}')
        # scope: health centers
        for name in health_centers.mappings.unique_short_names:
            region = health_centers.mappings.region[name]
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
            for name in health_centers.mappings.unique_short_names:
                entity = get_entity(name_key=name, date=date)
                for field in health_centers.dataclass.Numbers.__annotations__.keys():
                    if entity is None:
                        columns.append(None)
                    else:
                        columns.append(getattr(entity.numbers, field))
            writer.writerow(columns)

    logging.info('Writing CSV timestamp...')
    with open(f'{health_centers_csv}.timestamp', 'w') as timestamp_file:
        timestamp = int(time.time())
        timestamp_file.write(f'{timestamp}\n')

    logging.info('Writing one dimensional output for easier checking/diff purposes...')
    check_csv = os.path.join(repo_root, 'csv/health_centers_check.csv')
    with open(check_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')
        for entity in entities:  # should be already sorted
            writer.writerow([
                entity.date,
                entity.name,
                entity.name_key,
                entity.sheet,
                entity.file.split('/')[-1],
                entity.numbers.examinations___medical_emergency,
                entity.numbers.examinations___suspected_covid,
                entity.numbers.phone_triage___suspected_covid,
                entity.numbers.tests___performed,
                entity.numbers.tests___positive,
                entity.numbers.sent_to___hospital,
                entity.numbers.sent_to___self_isolation
            ])


if __name__ == '__main__':
    main()
