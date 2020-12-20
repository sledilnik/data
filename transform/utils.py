import hashlib


def sha1sum(fname):
    h = hashlib.sha1()
    try:
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None
