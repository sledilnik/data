import datetime
import glob
import logging
import os
import time
from pathlib import Path

import pandas as pd
from xlrd import XLRDError

pd.options.display.width = 300
pd.options.display.max_colwidth = 50
pd.options.display.max_columns = 40

age_groups = [
    "0-4",
    "5-14",
    "15-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65-74",
    "75-84",
    "85+",
]


def dump_epi_tb4(datum=None, *, data_loc="./data", output_dir=None, original_csv=None, new_csv=None,
                 diff_name="diff_log.csv", verbose="WARNING"):
    """Dump data from source_csv into a rainbow of cumsum columns.

    Inputs are datum in ISO format, an Excel file with sheet named tb4, and
    optionally, a previously parsed data specified under the argument name
    original_csv. If original_csv is specified, a diff file will be created
    indicating differences between new imported data and existing data. The last
    line, which should indicate what new has been added (and not modified) doesn't
    show a difference, but an absolute (cumulative) value.

    Output is a newly created csv.

    Usage:

        # from python

        dump_epi_tb4(datum="2020-11-01", original_csv="epi_tb4_dump_2020-10-31.csv")

    This will parse and compare data from November 1st to parsed data from October
    31st. This assumes the data is located in the same spot where Python script was
    called from. If you have data in a different spot, please use ``data_loc`` argument.

        # from command line

        python parse_tb4.py 2020-11-01 --original-csv=epi_tb4_dump_2020-10-31.csv

    Same as above, except the command is run from the command line.

    :param datum: Datum in ISO format (i.e. 2020-10-26). If omitted, it is assumed the
      date will be from yesterday.
    :param data_loc: Working directory where files are to be located if not located
      where the script was run from.
    :param output_dir: Where files will be stored. Diff will still be saved in the
      current working directory. Default is to write to csv/ folder of this repository.
    :param original_csv: A csv file that has been created in the previous run of the
      script. This file may not exist and it's fine, just leave it blank.
    :param new_csv: Name of the resulting file. Default is "latest_dump_tb4.csv,
      but can be anything, really.
    :param diff_name: Name of the diff log to be saved.
    :param verbose: Level of logging, see https://docs.python.org/3/library/logging.html#logging-levels
      for levels of logging available.
    """

    # Algorithm to give you the general idea of what this function is suppose to do:
    #
    # inputs:
    #   <date>
    # implicit inputs:
    #   <original_csv>
    #   <xlsx>
    #
    # 1: <xlsx> checks
    #   - based on date provided, find corresponding <xlsx> file. If missing yield
    #     informative error if file is not found (directions on how to structure the
    #     filename)
    #   - check that tb4 sheet exists with informative message on how to format the
    #     sheet name
    # 2: data integrity check
    #   - expect first column to be date and monotinically increasing/decreasing
    #   - expect columns 2:11 to be counts for age groups 0-85+ for men
    #   - expect columns 13:22 to be counts for age groups 0-85+ for women
    #   - all values for columns 2:22 should be >= 0 or NA (empty)
    # 3: missing dates
    #   - if any missing dates, ask user if assuming NA is ok
    #     - if ok, add missing dates NA for all columns
    #     - if not, abort
    # 4: calculate sums
    #   - calculate cumulative sums per age group per gender (20 new variables)
    #   - calculate row-wise age group sums (irrespective of gender) of cumulative sums
    #     (10 new variables)
    #   - calculate row-wise sums for each gender of cumulative sums (2 new variables)
    #   - calculate grand row-sums for genders combined of cumulative sums (1 new
    #     variable)
    #
    # output of the script is these new 34 variables (<new_csv>) and should not
    # overwrite <original_csv>
    #
    # 5: diff
    #   - create a log of differences between <original_csv> and new table created in 4
    #   - create a heatmap showing potential differences between <original_csv> and
    #     <new_csv>

    logging.basicConfig(level=verbose)
    logger = logging.getLogger(__file__.split("/")[-1])

    logger.debug(f"Entered datum: {datum}")
    # It's actually yesterday because data comes in with one day delay.
    today = datetime.datetime.today() - datetime.timedelta(days=1)

    data_loc = Path(data_loc)
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = Path("../csv")

    if not datum:
        datum = today.strftime("%Y-%m-%d")
        logger.info("Assuming datum to be today.")

    dt_datum = datetime.datetime.strptime(datum, "%Y-%m-%d")

    if not new_csv:
        new_csv = output_dir / "newest-age-confirmed.csv"
        logger.info(f"Assuming new_csv to be {new_csv}.")

    if not original_csv:
        original_csv = output_dir / "age-confirmed.csv"
        logger.info(f"Assuming original_csv to be {original_csv}.")

    input_datum = dt_datum.strftime("%d%m%Y")

    xlsx = glob.glob(pathname=f"{str(data_loc)}/*{input_datum}*")
    logger.debug(f"Found {len(xlsx)} .xlsx files.")
    # 1: <xlsx> checks
    #   - based on date provided, find corresponding <xlsx> file. If missing yield
    #     informative error if file is not found (directions on how to structure the
    #     filename)
    #   - check that tb4 sheet exists with informative message on how to format the
    #     sheet name
    if len(xlsx) == 0:
        raise FileNotFoundError("Found no files using this date-data_loc combination.")
    elif len(xlsx) > 1:
        raise FileExistsError(
            f"Found more than one file with datum {input_datum} in its name. Have only one file per datum."
        )
    else:
        xlsx = xlsx[0]

    if not os.path.isfile(xlsx):
        raise FileNotFoundError(f"Unable to find file with datum {input_datum} in its name.")

    age_groups_male = [f"{x}m" for x in age_groups]
    age_groups_female = [f"{x}f" for x in age_groups]

    custom_column_names = ["datum"]
    custom_column_names.extend(age_groups_male)
    custom_column_names.extend(age_groups_female)

    # Create a list of column indices and exclude SKUPAJ for men and women,
    # respectively.
    custom_column_indices = list(range(23))
    custom_column_indices.pop(11)
    custom_column_indices.pop(-1)

    try:
        xy = pd.read_excel(
            xlsx,
            header=0,
            sheet_name="tb4",
            skiprows=[0, 1],
            parse_dates=True,
            names=custom_column_names,
            usecols=custom_column_indices,
            converters=dict((i, int) for i in range(len(custom_column_indices)) if i > 0),
            skipfooter=1,  # skips the SKUPAJ row at the end
        )
        xy["datum"] = pd.to_datetime(xy["datum"])
    except XLRDError as xe:
        raise XLRDError(
            f"Unable to find sheet named tb4. Please examine {xlsx} if the sheet name has been spelled correctly."
        )
    except ValueError as ve:
        raise ValueError(
            "Chances are that one of your 'integers' is not an integer after all. Check data for " "incorrect entries."
        )

    logger.debug(f"Successfully imported file {xlsx}.")

    # 2: data integrity check
    #   - expect first column to be date and monotinically increasing/decreasing
    if not xy[xy["datum"].diff().dt.days < 0].empty:
        raise ValueError(
            "Datums are monotonically increasing. Please check the datum column to " "see if dates are in order."
        )

    #   - expect columns 2:11 to be counts for age groups 0-85+ for men
    #   - expect columns 13:22 to be counts for age groups 0-85+ for women
    # This is resolved on import using `converters`.

    #   - all values for columns 2:22 should be >= 0 or NA (empty)
    expect_counts = xy.iloc[:, 1 : len(xy.columns)]
    expect_counts_gezero = expect_counts >= 0
    expect_counts_null = expect_counts.isnull()
    counts_or_nan = expect_counts_gezero.__or__(expect_counts_null)

    bad_indices = xy.loc[~counts_or_nan.all(axis=1)]
    if len(bad_indices) > 0:
        raise ValueError(f"Some counts are not greater than 0 or are not NaN. Hint:\n\n" f"{bad_indices}")

    logger.debug(f"Found no negative counts.")

    xyall = pd.DataFrame({"datum": pd.date_range(start=xy["datum"].min(), end=xy["datum"].max())})

    # 3: missing dates
    #   - if any missing dates, ask user if assuming NA is ok
    #     - if ok, add missing dates NA for all columns
    #     - if not, abort
    if xyall.shape[0] != xy.shape[0]:
        logger.debug("Imputing missing data.")
        xy = xyall.merge(xy, how="left", on="datum")

    # Add 0 to missing fieds in order for the cumsum function to output expected result.
    # If this is not done, the missing values create a gap in cumulated sum.
    xy = xy.fillna(0)

    # 4: calculate sums
    #   - calculate cumulative sums per age group per gender (20 new variables)
    cs = xy.iloc[:, 1 : len(xy.columns)].cumsum(axis=None)
    #   - calculate row-wise age group sums (irrespective of gender) of cumulative
    #   sums (10 new variables)
    row_group_sums = []  # row-wise group sums
    for age_group in age_groups:
        tmp_cs = cs.filter(regex=age_group)
        tmp_cs = tmp_cs.sum(axis=1)
        tmp_cs.name = age_group
        tmp_cs = pd.DataFrame(tmp_cs)
        row_group_sums.append(tmp_cs)
    row_group_sums = pd.concat(row_group_sums, axis=1)
    logger.info("Calculated row-wise group sums.")

    #   - calculate row-wise sums for each gender of cumulative sums (2 new variables)
    rowsums_by_gender = []  # row-wise group sums by gender
    for gender, age_group in zip(["male", "female"], [age_groups_male, age_groups_female]):
        tmp_cs = cs[age_group].sum(axis=1)
        tmp_cs.name = gender
        tmp_cs = pd.DataFrame(tmp_cs)
        rowsums_by_gender.append(tmp_cs)
    rowsums_by_gender = pd.concat(rowsums_by_gender, axis=1)
    logger.info("Calculated row-wise sums by gender")

    #   - calculate grand row-sums for genders combined of cumulative sums (1 new
    #     variable)
    grs = rowsums_by_gender.sum(axis=1)
    grs.name = "grand_total"
    grs = pd.DataFrame(grs)
    logger.info("Calculated grand row sums.")

    out = pd.concat([xy.iloc[:, 0], cs, row_group_sums, rowsums_by_gender, grs], axis=1)

    out.to_csv(path_or_buf=str(new_csv), sep="\t", index=False)
    logger.debug(f"Wrote data into {new_csv}.")

    # Create a diff report on things that might have changed from the previous data
    # dump.
    if original_csv.exists():
        xyo = pd.read_csv(original_csv, sep="\t", parse_dates=False)
        ml_orig = pd.melt(xyo, id_vars="datum", var_name="class", value_name="count")

        ml_cur = pd.melt(out, id_vars="datum", var_name="class", value_name="count")
        ml_cur["datum"] = ml_cur["datum"].astype(str)

        ml = pd.merge(
            left=ml_cur,
            right=ml_orig,
            how="outer",
            on=["datum", "class"],
            suffixes=["_new", "_old"],
        )

        diff = ml[ml["count_new"] != ml["count_old"]].copy()
        diff["diff"] = diff["count_new"] - diff["count_old"]
        # Because original_csv doesn't have new_csv entries, the result is NaN. These
        # values need to be replaced with the new_csv entries.
        nulldiff = diff["diff"].isnull()
        diff.loc[nulldiff, "diff"] = diff.loc[nulldiff, "count_new"]

        diff = pd.pivot(diff, index="datum", columns="class", values="diff")
        diff.reset_index(inplace=True)
        diff = diff[out.columns]

        diff.to_csv(path_or_buf=diff_name, sep="\t", index=False)
        logger.warning(f"Wrote diff into {diff_name}.")

    new_csv.rename(target=original_csv)

    update_time = int(time.time())

    timestamp = output_dir / original_csv.name

    with open(f"{timestamp}.timestamp", "w") as f:
        f.write(str(update_time))

    logger.info(f"Successfully created {new_csv}.")
