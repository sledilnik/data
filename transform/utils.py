#!/usr/bin/env python

import hashlib
import os
import pyquery
import requests
import tempfile
import time
import urllib


def sha1sum(fname):
    h = hashlib.sha1()
    try:
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None


def write_timestamp_file(filename: str, old_hash: str):
    if old_hash != sha1sum(filename):
        with open(f'{filename}.timestamp', 'w', newline='') as f:
            f.write(f'{int(time.time())}\n')


def download_nijz_xslx_file(download_folder: str, search_for: str):

    def get_nijz_xlsx_url(search_for: str):
        pq = pyquery.PyQuery(requests.get(
            url='https://www.nijz.si/sl/dnevno-spremljanje-okuzb-s-sars-cov-2-covid-19',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}
        ).text)
        for x in pq('a').items():
            href = x.attr['href']
            if href and search_for in href:
                return 'https://www.nijz.si' + href

    url = get_nijz_xlsx_url(search_for=search_for)
    filename = url.split('/')[-1]
    path_file = os.path.join(download_folder, filename)

    if filename in os.listdir(download_folder):
        _, temp = tempfile.mkstemp()
        try:
            urllib.request.urlretrieve(url, temp)
            if sha1sum(path_file) == sha1sum(temp):
                print('Latest file already downloaded:', filename)
            else:
                os.rename(path_file, path_file.replace('.xlsx', f'.replaced.{int(time.time())}.xlsx'))
                urllib.request.urlretrieve(url, path_file)
                print('File with that name was already present, but was outdated. Old version is replaced. New version downloaded:', filename)
        finally:
            try:
                os.remove(temp)
            except:
                pass
    else:
        urllib.request.urlretrieve(url, path_file)
        print('Downloaded:', filename)
