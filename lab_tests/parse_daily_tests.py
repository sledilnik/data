#!/usr/bin/env python

import datetime
import logging
from pathlib import Path
import re
import time

from clize import run
import numpy as np
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 400)


def parse_daily_tests(
    path="./data", *, xlsx=None, output_folder="../csv", verbose="ERROR"
):
    """Parse daily testing reports to a comma separated file.

    Take in an Excel file with several tabs, and parse the 'podatki'
    sheet into a comma separated flat file. File contains several
    columns for various laboratories, their cumulative sums and some
    additional columns for regular testing and testing done during the
    course of National COVID-19 study.

    :parameter path: Path where to look for files
    :parameter xlsx: Relative or absolute path to the .xsl(x) file to be parsed
    :parameter output_folder: Location where to drop output files
    :parameter verbose: Level of logging, see https://docs.python.org/3/library/logging.html#logging-levels
      for levels of logging available.
    :return: Side effect is a parsed comma separated file in the ./csv project
      folder.
    """

    logging.basicConfig(level=verbose)
    logger = logging.getLogger(__file__.split("/")[-1])

    INPUT = Path(path)
    OUTPUT = Path(output_folder)

    logger.debug(f"Input folder is {str(INPUT)}")
    logger.debug(f"Writing will be done to {str(OUTPUT)}")

    if not xlsx:
        # If no xlsx file is provided, `path` folder is searched for excel files and parsed for datum. Latest file by
        # date is used for parsing.
        find_xlsxs = list(INPUT.glob(pattern="*.xlsx"))
    else:
        find_xlsxs = [INPUT / xlsx]

    logger.info(f"Found {len(find_xlsxs)} .xlsx files")

    datums = []
    for xlsx in find_xlsxs:
        find_date = re.search(r"^.*(\d{4}-\d{1,2}-\d{1,2})\.xlsx$", str(xlsx))
        datums.append(find_date.group(1))
    available_files = pd.DataFrame.from_dict(
        {"filename": [str(x) for x in find_xlsxs], "date": datums}
    )
    available_files["date"] = pd.to_datetime(available_files["date"]).dt.date
    available_files = available_files.sort_values(by="date", ascending=False)
    available_files = available_files.iloc[0,]
    xlsx = available_files["filename"]

    logger.info(f"Processing file {xlsx}")

    custom_column_names = [
        "date",
        "tests.lab.imi.performed",
        "tests.lab.imi.positive",
        "tests.lab.nlzohmb.performed",
        "tests.lab.nlzohmb.positive",
        "tests.lab.nlzohlj.performed",
        "tests.lab.nlzohlj.positive",
        "tests.lab.ukg.performed",
        "tests.lab.ukg.positive",
        "tests.lab.nlzohkp.performed",
        "tests.lab.nlzohkp.positive",
        "tests.lab.nlzohnm.performed",
        "tests.lab.nlzohnm.positive",
        "tests.lab.sbce.performed",
        "tests.lab.sbce.positive",
        "tests.lab.nlzohkr.performed",
        "tests.lab.nlzohkr.positive",
        "tests.lab.sbng.performed",
        "tests.lab.sbng.positive",
        "tests.lab.sbsg.performed",
        "tests.lab.sbsg.positive",
        "tests.lab.nlzohms.performed",
        "tests.lab.nlzohms.positive",
        "tests.regular.performed",
        "tests.regular.positive",
        "tests.ns-apr20.performed",
        "tests.ns-apr20.positive",
    ]

    custom_column_indices = list(range(30))
    custom_column_indices.pop(27)
    custom_column_indices.pop(26)
    custom_column_indices.pop(0)

    xy = pd.read_excel(
        xlsx,
        header=0,
        sheet_name="podatki",
        skiprows=[0, 1, 2, 3],
        parse_dates=True,
        names=custom_column_names,
        usecols=custom_column_indices,
        converters=dict((i, int) for i in range(len(custom_column_indices)) if i > 0),
        skipfooter=1,  # skips the SKUPAJ row at the end
    )

    logger.info(f"Imported {len(xy.index)} rows")

    # Some dates are invalid and we need to prepare them before parsing.
    for index, value in xy.iterrows():
        interval = xy.loc[index, "date"]

        if not isinstance(interval, datetime.datetime):
            # Catch any datum with a star at the end.
            interval = re.sub(pattern=r"\*$", repl="", string=interval)

            try:
                end_datum = datetime.datetime.strptime(interval, "%d.%m.%Y")
                xy.loc[index, "date"] = end_datum
                continue
            except ValueError:
                pass

            try:
                end_datum = interval.split("-")[1]
                end_datum = datetime.datetime.strptime(end_datum, "%d.%m.%Y")
                xy.loc[index, "date"] = end_datum
                continue
            except IndexError:
                pass

    xy["date"] = pd.to_datetime(xy["date"]).dt.date

    # The table comes with dates in the future. Since some cells may be polluted,
    # the easiest thing to do is to remove them using the file datum.
    xy = xy[xy["date"] <= available_files["date"]]
    logger.warning(f"File truncated to data <= {available_files['date']}")

    # Regular tests and national study
    # tests.regular.performed
    # tests.regular.performed.todate
    xy["tests.regular.performed.todate"] = xy["tests.regular.performed"].fillna(value=0)
    xy["tests.regular.performed.todate"] = xy["tests.regular.performed.todate"].cumsum()
    # tests.regular.positive
    # tests.regular.positive.todate
    xy["tests.regular.positive.todate"] = xy["tests.regular.positive"].fillna(value=0)
    xy["tests.regular.positive.todate"] = xy["tests.regular.positive.todate"].cumsum()

    # tests.ns-apr20.performed
    # tests.ns-apr20.performed.todate
    xy["tests.ns-apr20.performed.todate"] = xy["tests.ns-apr20.performed"].fillna(
        value=0
    )
    xy["tests.ns-apr20.performed.todate"] = xy[
        "tests.ns-apr20.performed.todate"
    ].cumsum()
    # tests.ns-apr20.positive
    # tests.ns-apr20.positive.todate
    xy["tests.ns-apr20.positive.todate"] = xy["tests.ns-apr20.positive"].fillna(value=0)
    xy["tests.ns-apr20.positive.todate"] = xy["tests.ns-apr20.positive.todate"].cumsum()

    # Totals
    xy["tests.performed"] = xy["tests.regular.performed"].fillna(value=0) + xy[
        "tests.ns-apr20.performed"
    ].fillna(value=0)
    xy["tests.performed.todate"] = xy["tests.performed"].cumsum()
    xy["tests.positive"] = xy["tests.regular.positive"].fillna(value=0) + xy[
        "tests.ns-apr20.positive"
    ].fillna(value=0)
    xy["tests.positive.todate"] = xy["tests.positive"].cumsum()

    # Per lab
    # tests.lab.<id>.performed.todate
    # tests.lab.<id>.performed
    # tests.lab.<id>.positive.todate
    # tests.lab.<id>.positive
    xy["tests.lab.imi.performed.todate"] = xy["tests.lab.imi.performed"].fillna(value=0)
    xy["tests.lab.imi.performed.todate"] = xy["tests.lab.imi.performed.todate"].cumsum()
    xy["tests.lab.imi.positive.todate"] = xy["tests.lab.imi.positive"].fillna(value=0)
    xy["tests.lab.imi.positive.todate"] = xy["tests.lab.imi.positive.todate"].cumsum()

    xy["tests.lab.nlzohmb.performed.todate"] = xy["tests.lab.nlzohmb.performed"].fillna(
        value=0
    )
    xy["tests.lab.nlzohmb.performed.todate"] = xy[
        "tests.lab.nlzohmb.performed.todate"
    ].cumsum()
    xy["tests.lab.nlzohmb.positive.todate"] = xy["tests.lab.nlzohmb.positive"].fillna(
        value=0
    )
    xy["tests.lab.nlzohmb.positive.todate"] = xy[
        "tests.lab.nlzohmb.positive.todate"
    ].cumsum()

    xy["tests.lab.nlzohlj.performed.todate"] = xy["tests.lab.nlzohlj.performed"].fillna(
        value=0
    )
    xy["tests.lab.nlzohlj.performed.todate"] = xy[
        "tests.lab.nlzohlj.performed.todate"
    ].cumsum()
    xy["tests.lab.nlzohlj.positive.todate"] = xy["tests.lab.nlzohlj.positive"].fillna(
        value=0
    )
    xy["tests.lab.nlzohlj.positive.todate"] = xy[
        "tests.lab.nlzohlj.positive.todate"
    ].cumsum()

    xy["tests.lab.ukg.performed.todate"] = xy["tests.lab.ukg.performed"].fillna(
        value=0
    )
    xy["tests.lab.ukg.performed.todate"] = xy[
        "tests.lab.ukg.performed.todate"
    ].cumsum()
    xy["tests.lab.ukg.positive.todate"] = xy["tests.lab.ukg.positive"].fillna(
        value=0
    )
    xy["tests.lab.ukg.positive.todate"] = xy[
        "tests.lab.ukg.positive.todate"
    ].cumsum()

    xy["tests.lab.nlzohkp.performed.todate"] = xy["tests.lab.nlzohkp.performed"].fillna(
        value=0
    )
    xy["tests.lab.nlzohkp.performed.todate"] = xy[
        "tests.lab.nlzohkp.performed.todate"
    ].cumsum()
    xy["tests.lab.nlzohkp.positive.todate"] = xy["tests.lab.nlzohkp.positive"].fillna(
        value=0
    )
    xy["tests.lab.nlzohkp.positive.todate"] = xy[
        "tests.lab.nlzohkp.positive.todate"
    ].cumsum()

    xy["tests.lab.nlzohnm.performed.todate"] = xy["tests.lab.nlzohnm.performed"].fillna(
        value=0
    )
    xy["tests.lab.nlzohnm.performed.todate"] = xy[
        "tests.lab.nlzohnm.performed.todate"
    ].cumsum()
    xy["tests.lab.nlzohnm.positive.todate"] = xy["tests.lab.nlzohnm.positive"].fillna(
        value=0
    )
    xy["tests.lab.nlzohnm.positive.todate"] = xy[
        "tests.lab.nlzohnm.positive.todate"
    ].cumsum()

    xy["tests.lab.sbce.performed.todate"] = xy["tests.lab.sbce.performed"].fillna(
        value=0
    )
    xy["tests.lab.sbce.performed.todate"] = xy[
        "tests.lab.sbce.performed.todate"
    ].cumsum()
    xy["tests.lab.sbce.positive.todate"] = xy["tests.lab.sbce.positive"].fillna(value=0)
    xy["tests.lab.sbce.positive.todate"] = xy["tests.lab.sbce.positive.todate"].cumsum()

    xy["tests.lab.nlzohkr.performed.todate"] = xy["tests.lab.nlzohkr.performed"].fillna(
        value=0
    )
    xy["tests.lab.nlzohkr.performed.todate"] = xy[
        "tests.lab.nlzohkr.performed.todate"
    ].cumsum()
    xy["tests.lab.nlzohkr.positive.todate"] = xy["tests.lab.nlzohkr.positive"].fillna(
        value=0
    )
    xy["tests.lab.nlzohkr.positive.todate"] = xy[
        "tests.lab.nlzohkr.positive.todate"
    ].cumsum()

    xy["tests.lab.sbng.performed.todate"] = xy["tests.lab.sbng.performed"].fillna(
        value=0
    )
    xy["tests.lab.sbng.performed.todate"] = xy[
        "tests.lab.sbng.performed.todate"
    ].cumsum()
    xy["tests.lab.sbng.positive.todate"] = xy["tests.lab.sbng.positive"].fillna(value=0)
    xy["tests.lab.sbng.positive.todate"] = xy["tests.lab.sbng.positive.todate"].cumsum()

    xy["tests.lab.sbsg.performed.todate"] = xy["tests.lab.sbsg.performed"].fillna(
        value=0
    )
    xy["tests.lab.sbsg.performed.todate"] = xy[
        "tests.lab.sbsg.performed.todate"
    ].cumsum()
    xy["tests.lab.sbsg.positive.todate"] = xy["tests.lab.sbsg.positive"].fillna(value=0)
    xy["tests.lab.sbsg.positive.todate"] = xy["tests.lab.sbsg.positive.todate"].cumsum()

    xy["tests.lab.nlzohms.performed.todate"] = xy["tests.lab.nlzohms.performed"].fillna(
        value=0
    )
    xy["tests.lab.nlzohms.performed.todate"] = xy[
        "tests.lab.nlzohms.performed.todate"
    ].cumsum()
    xy["tests.lab.nlzohms.positive.todate"] = xy["tests.lab.nlzohms.positive"].fillna(
        value=0
    )
    xy["tests.lab.nlzohms.positive.todate"] = xy[
        "tests.lab.nlzohms.positive.todate"
    ].cumsum()

    xy = xy[
        [
            "date",
            "tests.performed",
            "tests.performed.todate",
            "tests.positive",
            "tests.positive.todate",
            "tests.regular.performed",
            "tests.regular.performed.todate",
            "tests.regular.positive",
            "tests.regular.positive.todate",
            "tests.ns-apr20.performed",
            "tests.ns-apr20.performed.todate",
            "tests.ns-apr20.positive",
            "tests.ns-apr20.positive.todate",
            "tests.lab.imi.performed",
            "tests.lab.imi.performed.todate",
            "tests.lab.imi.positive",
            "tests.lab.imi.positive.todate",
            "tests.lab.nlzohmb.performed",
            "tests.lab.nlzohmb.performed.todate",
            "tests.lab.nlzohmb.positive",
            "tests.lab.nlzohmb.positive.todate",
            "tests.lab.nlzohlj.performed",
            "tests.lab.nlzohlj.performed.todate",
            "tests.lab.nlzohlj.positive",
            "tests.lab.nlzohlj.positive.todate",
            "tests.lab.ukg.performed",
            "tests.lab.ukg.performed.todate",
            "tests.lab.ukg.positive",
            "tests.lab.ukg.positive.todate",
            "tests.lab.nlzohkp.performed",
            "tests.lab.nlzohkp.performed.todate",
            "tests.lab.nlzohkp.positive",
            "tests.lab.nlzohkp.positive.todate",
            "tests.lab.nlzohnm.performed",
            "tests.lab.nlzohnm.performed.todate",
            "tests.lab.nlzohnm.positive",
            "tests.lab.nlzohnm.positive.todate",
            "tests.lab.sbce.performed",
            "tests.lab.sbce.performed.todate",
            "tests.lab.sbce.positive",
            "tests.lab.sbce.positive.todate",
            "tests.lab.nlzohkr.performed",
            "tests.lab.nlzohkr.performed.todate",
            "tests.lab.nlzohkr.positive",
            "tests.lab.nlzohkr.positive.todate",
            "tests.lab.sbng.performed",
            "tests.lab.sbng.performed.todate",
            "tests.lab.sbng.positive",
            "tests.lab.sbng.positive.todate",
            "tests.lab.sbsg.performed",
            "tests.lab.sbsg.performed.todate",
            "tests.lab.sbsg.positive",
            "tests.lab.sbsg.positive.todate",
            "tests.lab.nlzohms.performed",
            "tests.lab.nlzohms.performed.todate",
            "tests.lab.nlzohms.positive",
            "tests.lab.nlzohms.positive.todate",
        ]
    ]

    # For aesthetic reasons, replace zeros with NaNs.
    xy.replace(to_replace=0, value=np.nan, inplace=True)

    output_file = OUTPUT / "lab-tests.csv"
    xy.to_csv(path_or_buf=output_file, sep=",", index=False, float_format="%.0f")

    update_time = int(time.time())

    with open(f"{output_file}.timestamp", "w") as f:
        f.write(str(update_time))

    logger.info(f"Finished processing file")


if __name__ == "__main__":
    run(parse_daily_tests)
