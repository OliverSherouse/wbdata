import datetime as dt

import pytest

from wbdata import dates


def test_parse_year():
    assert dates._parse_year("2003") == dt.datetime(2003, 1, 1)


def test_parse_month():
    assert dates._parse_month("2003M12") == dt.datetime(2003, 12, 1)


def test_parse_quarter():
    assert dates._parse_quarter("2003Q2") == dt.datetime(2003, 4, 1)


@pytest.mark.parametrize(
    ["rows", "expected"],
    [
        pytest.param(
            [{"date": dt.datetime(2003, 1, 1)}, {"date": 5.26}],
            [{"date": dt.datetime(2003, 1, 1)}, {"date": 5.26}],
            id="not strings",
        ),
        pytest.param(
            [{"date": "2003"}, {"date": "2004"}],
            [{"date": dt.datetime(2003, 1, 1)}, {"date": dt.datetime(2004, 1, 1)}],
            id="years",
        ),
        pytest.param(
            [{"date": "2003M01"}, {"date": "2003M02"}],
            [{"date": dt.datetime(2003, 1, 1)}, {"date": dt.datetime(2003, 2, 1)}],
            id="months",
        ),
        pytest.param(
            [{"date": "2003Q1"}, {"date": "2003Q02"}],
            [{"date": dt.datetime(2003, 1, 1)}, {"date": dt.datetime(2003, 4, 1)}],
            id="quarters",
        ),
        pytest.param(
            [{"date": "MRV"}, {"date": "-"}],
            [{"date": "MRV"}, {"date": "-"}],
            id="MRV and dash",
        ),
        pytest.param(
            [{"date": "2003M1"}, {"date": "MRV"}, {"date": "-"}, {"date": 2003}],
            [
                {"date": dt.datetime(2003, 1, 1)},
                {"date": "MRV"},
                {"date": "-"},
                {"date": 2003},
            ],
            id="sneaky values",
        ),
    ],
)
def test_parse_row_dates(rows, expected):
    dates.parse_row_dates(rows)
    assert rows == expected


@pytest.mark.parametrize(
    ["date", "freq", "expected"],
    [
        pytest.param(dt.datetime(2003, 5, 1), "Y", "2003", id="year"),
        pytest.param(dt.datetime(2003, 5, 1), "M", "2003M05", id="month"),
        pytest.param(dt.datetime(2003, 5, 1), "Q", "2003Q2", id="quarter"),
    ],
)
def test_format_date(date, freq, expected):
    assert dates._format_date(date=date, freq=freq) == expected


def test_bad_format_date():
    with pytest.raises(ValueError, match=r"Unknown Frequency type"):
        dates._format_date(date=dt.datetime(2000, 1, 1), freq="Foobar")


@pytest.mark.parametrize(
    ["date", "expected"],
    [
        pytest.param(dt.datetime(2003, 4, 5), dt.datetime(2003, 4, 5), id="datetime"),
        pytest.param("2003", dt.datetime(2003, 1, 1), id="year"),
        pytest.param("2003M05", dt.datetime(2003, 5, 1), id="month"),
        pytest.param("2003Q2", dt.datetime(2003, 4, 1), id="quarter"),
        pytest.param("Feb 3, 2025", dt.datetime(2025, 2, 3), id="dateparser"),
    ],
)
def test_parse_date(date, expected):
    assert dates._parse_date(date=date) == expected


def test_parse_bad_date():
    with pytest.raises(ValueError):
        dates._parse_date("Gobbledygook")


def test_parse_and_format_date():
    assert dates._parse_and_format_date("Nov 3, 2025", "Q") == "2025Q4"


@pytest.mark.parametrize(
    ["dates_", "freq", "expected"],
    [
        pytest.param(dt.datetime(2003, 4, 5), "Y", "2003", id="single datetime"),
        pytest.param("May 2018", "M", "2018M05", id="single string"),
        pytest.param(
            (
                dt.datetime(2004, 5, 6),
                dt.datetime(2005, 6, 7),
            ),
            "M",
            "2004M05:2005M06",
            id="two datetimes",
        ),
        pytest.param(
            ("2020M01", "2021M12"),
            "Q",
            "2020Q1:2021Q4",
            id="two strings",
        ),
    ],
)
def test_format_dates(dates_, freq, expected):
    assert dates.format_dates(dates_, freq) == expected
