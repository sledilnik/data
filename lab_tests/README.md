Laboratory tests
----------------

This script takes in daily reports which holds:

* number of tested samples per laboratory
* number of positively tested samples per laboratory
* number of tested samples for routine testing
* number of positively tested samples for routine testing
* number of total sampled and positive (routine + national study)
* number of tested samples in the Nactionalna raziskava COVID-19
* number of positively tested samples in the Nactionalna raziskava COVID-19

To get help on how to run the script, type (in terminal)

```bash
$ python parse_daily_tests.py --help
Usage: parse_daily_tests.py [OPTIONS] [path]

Parse daily testing reports to a comma separated file.

Take in an Excel file with several tabs, and parse the 'podatki' sheet into a
comma separated flat file. File contains several columns for various
laboratories, their cumulative sums and some additional columns for regular
testing and testing done during the course of National COVID-19 study.

Arguments:
  path             (default: ./data)

Options:
  --output-folder=STR
                   (default: ../csv)
  --verbose=STR    (default: ERROR)
  --xlsx=STR

Other actions:
  -h, --help      Show the help
```

To run the script using a specific file, do

```bash
python parse_daily_tests.py --xlsx ./data/path/to/file.xlsx
```

To run the script on the latest `.xlsx` file in `path`, do

```bash
python parse_daily_tests.py
```

# Testing
To run tests, you should be located in root folder of the repository. To run all tests do

```bash
python -m unittest tests.test_lab_data
```

or 

```bash
python -m unittest tests.test_lab_data.TestParsingTestsLab.test_default_run
```

to run only specific tests.