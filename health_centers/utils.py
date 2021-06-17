#!/usr/bin/env python

import hashlib
import os
import pathlib
import pickle
import time


def timeit(method):

    def timed(*args, **kw):
        time_start = time.time()
        result = method(*args, **kw)
        time_end = time.time()
        print(f'[Execution time {method.__name__} {time_end - time_start}s]')
        return result

    return timed


def get_file_hash(filename: str):
    with open(filename, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


local_cache_path = os.path.join(pathlib.Path().absolute(), 'local_cache/')
sheets_cache_path = os.path.join(local_cache_path, 'sheets')


def get_cache():
    pathlib.Path(local_cache_path).mkdir(exist_ok=True)

    if not pathlib.Path(sheets_cache_path).exists():
        with open(sheets_cache_path, 'wb') as f:
            pickle.dump({}, f)

    with open(sheets_cache_path, 'rb') as f:
        return pickle.load(f)


def set_cache(obj: dict):
    with open(sheets_cache_path, 'wb') as f:
        pickle.dump(obj, f)
