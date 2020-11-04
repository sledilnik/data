from filecmp import cmp
from pathlib import Path
from unittest import TestCase
from xlrd import XLRDError
from epi.epi_functions import dump_epi_tb4


class TestParsingTable4(TestCase):
    file_location = "./tests/files"

    def test_missing_datum(self):
        with self.assertRaises(FileNotFoundError):
            dump_epi_tb4(data_loc="./files")

    def test_missing_sheet(self):
        with self.assertRaises(XLRDError):
            dump_epi_tb4(datum="2020-10-24", data_loc=self.file_location, output_dir="./tests")

    def test_multiple_files(self):
        with self.assertRaises(FileExistsError):
            dump_epi_tb4(datum="2020-10-25", data_loc=self.file_location)

    def test_invalid_datum(self):
        with self.assertRaises(ValueError):
            dump_epi_tb4(datum="2020-357", data_loc=self.file_location)

    def test_nonnumeric_values(self):
        with self.assertRaises(ValueError):
            dump_epi_tb4(datum="2020-10-28", data_loc=self.file_location)

    def test_negative_count(self):
        with self.assertRaises(ValueError):
            dump_epi_tb4(datum="2020-10-29", data_loc=self.file_location)

    def test_diffs(self):
        data_root = Path(self.file_location)
        output_folder = Path(".")

        # Data cleanup needed before running tests.
        age_confirmed = output_folder / "age-confirmed.csv"
        diff = Path("diff_log.csv")

        # Clean before running a test.
        if age_confirmed.exists():
            age_confirmed.unlink()
        if diff.exists():
            diff.unlink()

        timestamp = output_folder / "age-confirmed.csv.timestamp"
        dump_epi_tb4(datum="2020-10-19", data_loc=self.file_location, output_dir=str(output_folder))
        self.assertTrue(cmp(output_folder / "age-confirmed.csv", "./tests/files/test_dump.csv"))
        self.assertTrue(timestamp.exists())

        dump_epi_tb4(datum="2020-10-20", data_loc=self.file_location, output_dir=str(output_folder))
        self.assertTrue(cmp("diff_log.csv", "./tests/files/test_clean_diff.csv"))
        if age_confirmed.exists():
            age_confirmed.unlink()

        dump_epi_tb4(datum="2020-10-20", data_loc=self.file_location, output_dir=str(output_folder))
        self.assertTrue(cmp("diff_log.csv", "./tests/files/test_clean_diff.csv"))

        dump_epi_tb4(datum="2020-10-21", data_loc=self.file_location, output_dir=str(output_folder))
        self.assertTrue(cmp("diff_log.csv", "./tests/files/test_messy_diff.csv"))

        # Clean before running a test.
        if age_confirmed.exists():
            age_confirmed.unlink()
        if diff.exists():
            diff.unlink()
        if timestamp.exists():
            timestamp.unlink()
