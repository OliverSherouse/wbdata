"""
Miscellaneous data utilities
"""
import datetime as dt
import re
from typing import Any, Dict, Sequence, Tuple, Union

import dateparser

PATTERN_YEAR = re.compile(r"\d{4}")
PATTERN_MONTH = re.compile(r"\d{4}M\d{1,2}")
PATTERN_QUARTER = re.compile(r"\d{4}Q\d{1,2}")

Date = Union[str, dt.datetime]
Dates = Union[Date, Tuple[Date, Date]]


def _parse_year(datestr: str) -> dt.datetime:
    """return datetime.datetime object from %Y formatted string"""
    return dt.datetime.strptime(datestr, "%Y")


def _parse_month(datestr: str) -> dt.datetime:
    """return datetime.datetime object from %YM%m formatted string"""
    split = datestr.split("M")
    return dt.datetime(int(split[0]), int(split[1]), 1)


def _parse_quarter(datestr: str) -> dt.datetime:
    """
    return datetime.datetime object from %YQ%# formatted string, where # is
    the desired quarter
    """
    split = datestr.split("Q")
    quarter = int(split[1])
    month = quarter * 3 - 2
    return dt.datetime(int(split[0]), month, 1)


def parse_row_dates(data: Sequence[Dict[str, Any]]) -> None:
    """
    Replace date strings in raw response with datetime objects, in-place.

    Does not replace "MRV" or "-". If we don't recognize the format, do nothing.

    Parameters:
        data: sequence of dictionaries with `date` keys to parse
    """
    first = data[0]["date"]
    if not isinstance(first, str):  # Ignore unexpected cases
        return
    if PATTERN_MONTH.match(first):
        converter = _parse_month
    elif PATTERN_QUARTER.match(first):
        converter = _parse_quarter
    else:
        converter = _parse_year
    for datum in data:
        datum_date = datum["date"]
        if not isinstance(datum_date, str) or "MRV" in datum_date or "-" in datum_date:
            continue
        datum["date"] = converter(datum_date)


def _format_date(date: dt.datetime, freq: str) -> str:
    """
    Convert date to the appropriate representation base on freq


    :date: A datetime.datetime object to be formatted
    :freq: One of 'Y' (year), 'M' (month) or 'Q' (quarter)

    """
    try:
        return {
            "Y": lambda x: x.strftime("%Y"),
            "M": lambda x: x.strftime("%YM%m"),
            "Q": lambda x: f"{x.year}Q{(x.month - 1) // 3 + 1}",
        }[freq](date)
    except KeyError as e:
        raise ValueError(f"Unknown Frequency type: {freq}") from e


def _parse_date(date: Date) -> dt.datetime:
    if isinstance(date, dt.datetime):
        return date
    if PATTERN_YEAR.fullmatch(date):
        return _parse_year(date)
    if PATTERN_MONTH.fullmatch(date):
        return _parse_month(date)
    if PATTERN_QUARTER.fullmatch(date):
        return _parse_quarter(date)
    last_chance = dateparser.parse(date)
    if last_chance:
        return last_chance
    raise ValueError(f"Unable to parse date string {date}")


def _parse_and_format_date(date: Date, freq: str) -> str:
    return _format_date(_parse_date(date), freq)


def format_dates(dates: Dates, freq: str) -> str:
    """
    Given one or two date arguments, turn them into WB-accepted date parameters

    Parameters:
        dates: a date or a tuple of two dates, where a date is either a string
            or a datetime.datetime object. The date can be either a World-Bank
            format string or anything that dateparser can handle.
        freq: One of "Y", "M", or "Q" for year, month, or quarter respectively.

    Returns:
        A string representing a date or date range according to the specified
        frequency in the form the World Bank API expects.
    """
    if isinstance(dates, tuple):
        return (
            f"{_parse_and_format_date(dates[0], freq)}"
            f":{_parse_and_format_date(dates[1], freq)}"
        )
    return _parse_and_format_date(dates, freq)
