from pathlib import Path
from unittest import TestCase

import pandas as pd
from lab_tests.parse_daily_tests import parse_daily_tests


class TestParsingTestsLab(TestCase):
    file_location = Path("./tests/files")
    xy_file = Path("lab-tests.csv")
    xy_timestamp = Path("lab-tests.csv.timestamp")

    def test_default_run(self):
        parse_daily_tests(
            path=str(self.file_location),
            verbose="ERROR",
            output_folder=".",
        )
        xy = pd.read_csv(self.xy_file)
        self.assertEqual(list(xy.date)[-1], "2020-11-20")

        self.xy_file.unlink()
        self.xy_timestamp.unlink()

    def test_specified_xlsx(self):
        parse_daily_tests(
            path=str(self.file_location),
            output_folder=".",
            verbose="ERROR",
            xlsx="test results 2020-11-19.xlsx",
        )
        xy = pd.read_csv(self.xy_file)
        self.assertEqual(list(xy.date)[-1], "2020-11-19")

        self.xy_file.unlink()
        self.xy_timestamp.unlink()
