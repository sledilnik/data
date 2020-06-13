import logging
import os
import pathlib
import requests
import shutil
import zipfile

import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__.split('/')[-1])


def get_archive(dir: str, folder_id: str, file_id: str, password: str):
    url = f'{config.KOOFR_ROOT}content/links/{folder_id}/files/get/{file_id}?path=%2F&password={password}'
    logger.info(f'Fetching {url}')
    resp = requests.get(url, headers={'User-Agent': 'curl'})
    zip_path = os.path.join(dir, 'temp.zip')
    with open(zip_path, 'wb') as f:
        f.write(resp.content)
    logger.info('Extracting archive...')
    zipfile.ZipFile(zip_path).extractall(path=dir)
    pathlib.Path(zip_path).unlink()


def main():
    logger.info('Cleaning local cache folder...')
    shutil.rmtree(config.local_cache_dir, ignore_errors=True)
    pathlib.Path(config.local_cache_dir_zd).mkdir(parents=True)
    pathlib.Path(config.local_cache_dir_hos).mkdir()

    logger.info('Fetching archives...')
    get_archive(
        dir=config.local_cache_dir_hos,
        folder_id=config.KOOFR_ID_HOS,
        file_id='HOS.zip',
        password=config.KOOFR_PASS_HOS
    )
    get_archive(
        dir=config.local_cache_dir_zd,
        folder_id=config.KOOFR_ID_ZD,
        file_id='ZD.zip',
        password=config.KOOFR_PASS_ZD
    )


if __name__ == '__main__':
    main()
