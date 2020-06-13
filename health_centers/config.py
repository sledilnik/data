import os


KOOFR_ROOT = 'https://app.koofr.net/'
KOOFR_ID_ZD = 'b232782b-9893-4278-b54c-faf461fce4bd'
KOOFR_ID_HOS = '2c90ec11-f01e-4fb0-86fd-d430c1fff181'
KOOFR_PASS_ZD = os.getenv('ZD_ZIP_PASS')
assert KOOFR_PASS_ZD, 'Environmental variable ZD_ZIP_PASS must be set.'
KOOFR_PASS_HOS = os.getenv('HOS_ZIP_PASS')
assert KOOFR_PASS_HOS, 'Environmental variable HOS_ZIP_PASS must be set.'

health_centers_dir = os.path.dirname(os.path.abspath(__file__))
local_cache_dir = os.path.join(health_centers_dir, 'local_cache')
local_cache_dir_zd = os.path.join(local_cache_dir, 'zd')
local_cache_dir_hos = os.path.join(local_cache_dir, 'hos')
