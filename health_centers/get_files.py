import glob
import logging
import types

import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__.split('/')[-1])


def list_xlsx(dir: str):
    """ Lists all .xlsx files in a directory recursively.
    """
    return glob.glob(dir + '/**/*.xlsx', recursive=True)


def get_files(dir: str):
    logger.info('List of fetched .xlsx files:')
    files = list_xlsx(dir=dir)
    for f in files:
        logger.info(f.split('/')[-1])
    return files


def main():
    return types.SimpleNamespace(
        hos=get_files(dir=config.local_cache_dir_hos),
        zd=get_files(dir=config.local_cache_dir_zd)
    )


if __name__ == '__main__':
    main()
