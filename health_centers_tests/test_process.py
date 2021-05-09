#!/usr/bin/env python

import glob
import os


from health_centers.process import list_xlsx, get_sheet_hos, read_sheets


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def test_list_xlsx():
    actual = list_xlsx(dir=DATA_DIR)
    expected = [
        'health_centers_tests/data/HOS/Bolnišnice COVID 12052020 (copy).xlsx',
        'health_centers_tests/data/HOS/Bolnišnice COVID 12052020.xlsx',
        'health_centers_tests/data/HOS/2020-04/Bolnišnice COVID 30042020.xlsx'
    ]
    for a, e in zip(actual, expected):
        assert a.endswith(e)


def test_get_sheet_hos():
    sheet = get_sheet_hos(xlsx_file=os.path.join(DATA_DIR, 'HOS/Bolnišnice COVID 12052020.xlsx'))
    assert str(sheet) == '<Worksheet "Bolnišnice COVID točke">'

    sheet = get_sheet_hos(xlsx_file=os.path.join(DATA_DIR, 'HOS/2020-04/Bolnišnice COVID 30042020.xlsx'))
    assert sheet is None


def test_read_sheets():
    sheet = get_sheet_hos(xlsx_file=os.path.join(DATA_DIR, 'HOS/Bolnišnice COVID 12052020.xlsx'))
    sheet.file = 'HOS/Bolnišnice COVID 12052020.xlsx'
    read_sheets(sheets=[sheet])
    sheet = get_sheet_hos(xlsx_file=os.path.join(DATA_DIR, 'HOS/Bolnišnice COVID 12052020 (copy).xlsx'))
    sheet.file = 'HOS/Bolnišnice COVID 12052020 (copy).xlsx'
    read_sheets(sheets=[sheet])
