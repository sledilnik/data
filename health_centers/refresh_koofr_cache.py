import logging
import requests

from config import KOOFR_ROOT, KOOFR_ID_ZD, KOOFR_PASS_ZD, KOOFR_ID_HOS, KOOFR_PASS_HOS


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__.split('/')[-1])


def main():
    for url in [
        f'{KOOFR_ROOT}api/v2/public/links/{KOOFR_ID_ZD}/bundle?path=%2F&password={KOOFR_PASS_ZD}',
        f'{KOOFR_ROOT}api/v2/public/links/{KOOFR_ID_HOS}/bundle?path=%2F&password={KOOFR_PASS_HOS}'
    ]:
        logger.info(f'Fetching {url}')
        resp = requests.get(url, headers={'User-Agent': 'curl'})
        assert resp.status_code == 200, (url, resp.status_code)


if __name__ == '__main__':
    main()
