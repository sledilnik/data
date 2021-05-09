#!/usr/bin/env python

import glob
import logging
import os
import types


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__.split('/')[-1])


def list_xlsx(dir: str):
    """ Lists all .xlsx files in a directory recursively.
    """
    return glob.glob(dir + '/**/*.xlsx', recursive=True)


def get_files(dir: str):
    logger.debug('List of fetched .xlsx files:')
    files = list_xlsx(dir=dir)
    for f in files:
        logger.debug(f.split('/')[-1])
    return files


def main():

    covid_data_path = os.getenv('COVID_DATA_PATH')
    assert covid_data_path, 'COVID_DATA_PATH env variable must be set. (The location of the COVID-DATA folder)'

    assert_msg = f'{covid_data_path} does not contain ZD and HOS folders. Have you set the right COVID_DATA_PATH?'
    assert all(folder in os.listdir(covid_data_path) for folder in ['ZD', 'HOS']), assert_msg

    hos = get_files(dir=os.path.join(covid_data_path, 'HOS'))
    zd = get_files(dir=os.path.join(covid_data_path, 'ZD'))
    return types.SimpleNamespace(all=hos + zd, hos=hos, zd=zd)


if __name__ == '__main__':
    main()
