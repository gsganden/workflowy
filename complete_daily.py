import argparse
from datetime import datetime
import logging
from pathlib import Path
from xml.etree import ElementTree as ET


WORKFLOWY_OPML_INPATH = Path.home() / "Downloads" / "workflowy-export.opml"
DAILY_OPML_OUTPATH = Path.home() / "workflowy" / "daily.opml"
DAYS_OF_WEEK = ["mon", "tues", "wed", "thurs", "fri", "sat", "sun"]
ADDITIONAL_TAGS_TO_COMPLETE_BY_DOW = {
    "mon": ["@weekend"],
    "tues": ["@weekend", "@teachingday"],
    "wed": ["@weekend"],
    "thurs": ["@weekend", "@teachingday"],
    "fri": ["@weekend", "@teachingday"],
    "sat": ["@weekday", "@teachingday"],
    "sun": ["@weekday", "@teachingday"],
}


def main(day, wfh, holiday, away):
    outline = ET.parse(str(WORKFLOWY_OPML_INPATH))
    daily = _reduce_to_daily(outline)
    _complete(daily, day, wfh, holiday, away)
    outline.write(DAILY_OPML_OUTPATH)


def _reduce_to_daily(outline):
    root = outline.getroot()
    body = root.find("body")
    for item in body.findall("outline"):
        if "daily" in item.get("text").lower():
            daily = item
        else:
            body.remove(item)
    return daily


def _complete(daily, day, wfh, holiday, away):
    tags_to_complete = _get_tags_to_complete(day, wfh, holiday, away)

    for item in daily.getiterator():
        text = item.get("text")
        if text is not None:
            if any(tag in text for tag in tags_to_complete):
                item.attrib["_complete"] = "true"
            elif "_complete" in item.attrib:
                del item.attrib["_complete"]


def _get_tags_to_complete(day, wfh, holiday, away):
    tags_to_complete = [
        f"#{dow}" if dow == day else f"@{dow}" for dow in DAYS_OF_WEEK
    ] + ADDITIONAL_TAGS_TO_COMPLETE_BY_DOW[day]
    if wfh:
        tags_to_complete.append("#wfh")
    if holiday:
        tags_to_complete.append("#holiday")
    if away:
        tags_to_complete.append("#away")
    if "@weekday" in tags_to_complete and holiday:
        tags_to_complete += "@workday"
    if "@weekday" in tags_to_complete and (holiday or wfh):
        tags_to_complete += "@officeday"
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
    args = vars(parser.parse_args())
    logging.info(f"Arguments passed at command line: {args}")
    return args


def _get_tomorrow():
    tomorrow_num = datetime.today().weekday() + 1
    tomorrow = DAYS_OF_WEEK[tomorrow_num]
    return tomorrow


if __name__ == "__main__":
    args = _parse_args()
    main(**args)
