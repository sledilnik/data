import hashlib
import time


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
