import os
import subprocess


def get_parent_dir(abs_path):
    return os.path.abspath(os.path.join(abs_path, os.pardir))
repo_root = get_parent_dir(get_parent_dir(__file__))


def test_temp():
    output_actual_file = f'{repo_root}/tests/output_actual.csv'
    output_expected_file = f'{repo_root}/tests/output_expected.csv'
    assert not os.path.exists(output_actual_file)
    try:
        subprocess.check_output([
            'python', f'{repo_root}/process.py',
            '-d', 'porocilo_zd/',
            '-f', f'{repo_root}/tests/output_actual.csv'
        ])

        with open(output_expected_file, 'r') as expected, open(output_actual_file, 'r') as actual:
            lines_expected = expected.readlines()
            lines_actual = actual.readlines()
            assert len(lines_expected) == len(lines_actual)
            for expected, actual in zip(lines_expected, lines_actual):
                assert expected == actual
    except:
        raise
    finally:
        if os.path.exists(output_actual_file):
            os.remove(output_actual_file)
