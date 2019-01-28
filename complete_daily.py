"""
Tag notation:
# -- complete if this kind of day
@ -- complete if not this kind of day

Supported tags:
#/@ + mon tues wed thurs fri sat
@ + weekday, weekend
@/# teachingday
#wfh -- working from home
#holiday -- weekday off of work
#away -- not at home
@workday -- equivalent to @weekday #holiday
@officeday -- equivalent to @weekday #wfh #holiday
#temp -- temporary
"""

import argparse
from datetime import datetime
import logging
from pathlib import Path
import os
from xml.etree import ElementTree as ET


WORKFLOWY_OPML_INPATH = Path.home() / "Downloads" / "workflowy-export.opml"
DAILY_OPML_OUTPATH = Path.home() / "workflowy" / "daily.opml"
DAYS_OF_WEEK = ["mon", "tues", "wed", "thurs", "fri", "sat", "sun"]
ADDITIONAL_TAGS_TO_COMPLETE_BY_DOW = {
    "mon": ["@weekend"],
    "tues": ["@weekend"],
    "wed": ["@weekend"],
    "thurs": ["@weekend"],
    "fri": ["@weekend"],
    "sat": ["@weekday"],
    "sun": ["@weekday"],
}


def main(day, wfh, holiday, away, teaching):
    tags_to_complete = _get_tags_to_complete(day, wfh, holiday, away, teaching)
    query = ' OR '.join(tags_to_complete)
    print(f'Query: {query}')
    cmd = f'echo "{query}" | pbcopy'
    os.system(cmd)
    print('Query has been copied to clipboard')


def _get_tags_to_complete(day, wfh, holiday, away, teaching):
    tags_to_complete = [
        f"#{dow}" if dow == day else f"@{dow}" for dow in DAYS_OF_WEEK
    ] + ADDITIONAL_TAGS_TO_COMPLETE_BY_DOW[day]

    if wfh:
        tags_to_complete.append("#wfh")
    if holiday:
        tags_to_complete.append("#holiday")
    if away:
        tags_to_complete.append("#away")

    if teaching:
        tags_to_complete.append("#teaching")
    else:
        tags_to_complete.append("@teaching")

    if "@weekday" in tags_to_complete or holiday:
        tags_to_complete.append("@workday")
    if "@weekday" in tags_to_complete or holiday or wfh:
        tags_to_complete.append("@officeday")

    return tags_to_complete


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--day",
        "-d",
        type=str,
        help="Day of week to check off",
        choices=DAYS_OF_WEEK,
        default=_get_tomorrow(),
    )
    parser.add_argument("--wfh", action="store_true", help="Working from home ")
    parser.add_argument("--holiday", action="store_true", help="Weekday with no work")
    parser.add_argument("--away", action="store_true", help="Not at home")
    parser.add_argument("--teaching", action="store_true", help="Teaching")
    args = vars(parser.parse_args())
    logging.info(f"Arguments passed at command line: {args}")
    return args


def _get_tomorrow():
    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(logging.INFO)
    tomorrow_num = (datetime.today().weekday() + 1) % 7
    tomorrow = DAYS_OF_WEEK[tomorrow_num]
    return tomorrow


if __name__ == "__main__":
    args = _parse_args()
    main(**args)
