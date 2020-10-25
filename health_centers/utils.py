import time


def timeit(method):

    def timed(*args, **kw):
        time_start = time.time()
        result = method(*args, **kw)
        time_end = time.time()
        print(f'[Execution time {method.__name__} {time_end - time_start}s]')
        return result

    return timed
