import datetime as dt
import itertools
import re
from unittest import mock

import pandas as pd  # type: ignore[import-untyped]
import pytest

from wbdata import client, fetcher


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        pytest.param(
            [{"id": "USA", "name": "United States"}],
            "id    name\n----  -------------\nUSA   United States",
        ),
        pytest.param(
            [{"id": "WB", "value": "World Bank"}],
            "id    value\n----  ----------\nWB    World Bank",
        ),
    ],
)
def test_search_results_repr(data, expected):
    assert repr(client.SearchResult(data)) == expected


@pytest.mark.parametrize(
    ["arg", "expected"],
    [
        pytest.param("foo", "foo", id="string"),
        pytest.param(["foo", "bar", "baz"], "foo;bar;baz", id="list of strings"),
        pytest.param({1: "a", 2: "b", 3: "c"}, "1;2;3", id="dict of ints"),
        pytest.param(5.356, "5.356", id="float"),
    ],
)
def test_parse_value_or_iterable(arg, expected):
    assert client._parse_value_or_iterable(arg) == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        pytest.param("5.1", 5.1, id="float"),
        pytest.param("3", 3.0, id="int"),
        pytest.param("heloooo", None, id="non-numeric"),
    ],
)
def test_cast_float(value, expected):
    assert client._cast_float(value) == expected


@pytest.fixture
def mock_client():
    with mock.patch("wbdata.client.fetcher.Fetcher", mock.Mock):
        yield client.Client()


@pytest.mark.parametrize(
    [
        "kwargs",
        "expected_url",
        "expected_args",
    ],
    [
        pytest.param(
            {"indicator": "FOO"},
            "https://api.worldbank.org/v2/countries/all/indicators/FOO",
            {},
            id="simple",
        ),
        pytest.param(
            {"indicator": "FOO", "country": "USA"},
            "https://api.worldbank.org/v2/countries/USA/indicators/FOO",
            {},
            id="one country",
        ),
        pytest.param(
            {"indicator": "FOO", "country": ["USA", "GBR"]},
            "https://api.worldbank.org/v2/countries/USA;GBR/indicators/FOO",
            {},
            id="two countries",
        ),
        pytest.param(
            {"indicator": "FOO", "date": "2005M02"},
            "https://api.worldbank.org/v2/countries/all/indicators/FOO",
            {"date": "2005"},
            id="date",
        ),
        pytest.param(
            {"indicator": "FOO", "date": ("2006M02", "2008M10"), "freq": "Q"},
            "https://api.worldbank.org/v2/countries/all/indicators/FOO",
            {"date": "2006Q1:2008Q4"},
            id="date and freq",
        ),
        pytest.param(
            {"indicator": "FOO", "source": "1"},
            "https://api.worldbank.org/v2/countries/all/indicators/FOO",
            {"source": "1"},
            id="one source",
        ),
        pytest.param(
            {"indicator": "FOO", "skip_cache": True},
            "https://api.worldbank.org/v2/countries/all/indicators/FOO",
            {},
            id="skip cache true",
        ),
    ],
)
def test_get_data_args(mock_client, kwargs, expected_url, expected_args):
    mock_client.fetcher.fetch = mock.Mock(return_value="Foo")
    mock_client.get_data(**kwargs)
    mock_client.fetcher.fetch.assert_called_once_with(
        url=expected_url,
        params=expected_args,
        skip_cache=kwargs.get("skip_cache", False),
    )


def test_parse_dates(mock_client):
    expected = [{"date": dt.datetime(2023, 4, 1)}]
    mock_client.fetcher.fetch = mock.Mock(return_value=[{"date": "2023Q2"}])
    got = mock_client.get_data("foo", parse_dates=True)
    assert got == expected


@pytest.mark.parametrize(
    ["url", "id_", "skip_cache", "expected_url"],
    [
        pytest.param("https://foo.bar", None, False, "https://foo.bar", id="no id"),
        pytest.param(
            "https://foo.bar", "baz", False, "https://foo.bar/baz", id="one id"
        ),
        pytest.param(
            "https://foo.bar",
            ["baz", "bat"],
            False,
            "https://foo.bar/baz;bat",
            id="two ids",
        ),
        pytest.param("https://foo.bar", None, True, "https://foo.bar", id="nocache"),
    ],
)
def test_id_only_query(mock_client, url, id_, skip_cache, expected_url):
    mock_client.fetcher.fetch = mock.Mock(return_value=["foo"])
    got = mock_client._id_only_query(url, id_, skip_cache=skip_cache)
    assert list(got) == ["foo"]
    mock_client.fetcher.fetch.assert_called_once_with(
        url=expected_url, skip_cache=skip_cache
    )


@pytest.mark.parametrize(
    ["function", "id_", "skip_cache", "expected_url"],
    [
        (function, id_, skip_cache, f"{host}{path}")
        for ((function, host), (id_, path), skip_cache) in itertools.product(
            (
                ("get_sources", client.SOURCE_URL),
                ("get_incomelevels", client.ILEVEL_URL),
                ("get_topics", client.TOPIC_URL),
                ("get_lendingtypes", client.LTYPE_URL),
            ),
            (
                (None, ""),
                ("foo", "/foo"),
                (["foo", "bar"], "/foo;bar"),
            ),
            (True, False),
        )
    ],
)
def test_id_only_functions(mock_client, function, id_, skip_cache, expected_url):
    mock_client.fetcher.fetch = mock.Mock(return_value=["foo"])
    got = getattr(mock_client, function)(id_, skip_cache=skip_cache)
    assert list(got) == ["foo"]
    mock_client.fetcher.fetch.assert_called_once_with(
        url=expected_url, skip_cache=skip_cache
    )


@pytest.mark.parametrize(
    ["country_id", "incomelevel", "lendingtype", "path", "args", "skip_cache"],
    (
        (cid, il, ltype, path, {**il_args, **ltype_args}, skip_cache)  # type: ignore[dict-item]
        for (
            (cid, path),
            (il, il_args),
            (ltype, ltype_args),
            skip_cache,
        ) in itertools.product(
            (
                (None, ""),
                ("foo", "/foo"),
                (["foo", "bar"], "/foo;bar"),
            ),
            (
                (None, {}),
                (2, {"incomeLevel": "2"}),
                ([2, 3], {"incomeLevel": "2;3"}),
            ),
            (
                (None, {}),
                (4, {"lendingType": "4"}),
                ([4, 5], {"lendingType": "4;5"}),
            ),
            (True, False),
        )
        if cid is None or (il is None and ltype is None)
    ),
)
def test_get_countries(
    mock_client, country_id, incomelevel, lendingtype, path, args, skip_cache
):
    mock_client.fetcher.fetch = mock.Mock(return_value=["foo"])
    got = mock_client.get_countries(
        country_id=country_id,
        incomelevel=incomelevel,
        lendingtype=lendingtype,
        skip_cache=skip_cache,
    )
    assert list(got) == ["foo"]
    if country_id:
        mock_client.fetcher.fetch.assert_called_once_with(
            url=f"{client.COUNTRIES_URL}{path}", skip_cache=skip_cache
        )
    else:
        mock_client.fetcher.fetch.assert_called_once_with(
            url=f"{client.COUNTRIES_URL}{path}", params=args, skip_cache=skip_cache
        )


@pytest.mark.parametrize(
    ["kwargs"],
    (
        [{"country_id": "foo", "incomelevel": "bar"}],
        [{"country_id": "foo", "lendingtype": "bar"}],
    ),
)
def test_get_countries_bad(mock_client, kwargs):
    with pytest.raises(ValueError, match=r"country_id and aggregates"):
        mock_client.get_countries(**kwargs)


@pytest.mark.parametrize(
    ("indicator", "source", "topic", "skip_cache", "expected_url"),
    (
        ("foo", None, None, True, f"{client.INDICATOR_URL}/foo"),
        (["foo", "bar"], None, None, False, f"{client.INDICATOR_URL}/foo;bar"),
        (None, "foo", None, False, f"{client.SOURCE_URL}/foo/indicators"),
        (None, ["foo", "bar"], None, True, f"{client.SOURCE_URL}/foo;bar/indicators"),
        (None, None, "foo", False, f"{client.TOPIC_URL}/foo/indicators"),
        (None, None, ["foo", "bar"], True, f"{client.TOPIC_URL}/foo;bar/indicators"),
        (None, None, None, True, client.INDICATOR_URL),
    ),
)
def test_get_indicators(
    mock_client, indicator, source, topic, skip_cache, expected_url
):
    mock_client.fetcher.fetch = mock.Mock(return_value=[["foo"]])
    got = mock_client.get_indicators(
        indicator=indicator,
        source=source,
        topic=topic,
        skip_cache=skip_cache,
    )
    assert list(got) == [["foo"]]
    mock_client.fetcher.fetch.assert_called_once_with(
        url=expected_url,
        skip_cache=skip_cache,
    )


@pytest.mark.parametrize(
    ("indicator", "source", "topic"),
    (
        ("foo", "bar", None),
        ("foo", None, "baz"),
        ("foo", "bar", "baz"),
        (None, "foo", "bar"),
    ),
)
def test_get_indicator_indicator_and_facet(mock_client, indicator, source, topic):
    with pytest.raises(ValueError, match="Cannot specify"):
        mock_client.get_indicators(indicator=indicator, source=source, topic=topic)


@pytest.mark.parametrize(
    ("raw", "query", "expected"),
    (
        (
            [{"name": "United States"}, {"name": "Great Britain"}],
            "states",
            [{"name": "United States"}],
        ),
        (
            [{"name": "United States"}, {"name": "Great Britain"}],
            re.compile("states"),
            [],
        ),
    ),
)
def test_search_countries(mock_client, raw, query, expected):
    mock_client.fetcher.fetch = mock.Mock(return_value=raw)
    got = mock_client.get_countries(query=query)
    assert list(got) == expected


@pytest.mark.parametrize(
    ("raw", "query", "expected"),
    (
        (
            [{"name": "United States"}, {"name": "Great Britain"}],
            "states",
            [{"name": "United States"}],
        ),
        (
            [{"name": "United States"}, {"name": "Great Britain"}],
            re.compile("states"),
            [],
        ),
    ),
)
def test_search_indicators(mock_client, raw, query, expected):
    mock_client.fetcher.fetch = mock.Mock(return_value=raw)
    got = mock_client.get_indicators(query=query)
    assert list(got) == expected


def test_get_series_passthrough(mock_client):
    with mock.patch.object(
        mock_client,
        "get_data",
        mock.Mock(
            return_value=fetcher.Result(
                [{"country": {"value": "usa"}, "date": "2023", "value": "5"}]
            )
        ),
    ) as mock_get_data:
        kwargs = dict(
            indicator="foo",
            country="usa",
            date="2023",
            freq="Q",
            source="2",
            parse_dates=True,
            skip_cache=True,
        )
        mock_client.get_series(**kwargs)

        mock_get_data.assert_called_once_with(**kwargs)


@pytest.mark.parametrize(
    ["response", "keep_levels", "expected"],
    (
        pytest.param(
            fetcher.Result(
                [
                    {"country": {"value": "usa"}, "date": "2023", "value": "5"},
                    {"country": {"value": "usa"}, "date": "2024", "value": "6"},
                    {"country": {"value": "gbr"}, "date": "2023", "value": "7"},
                    {"country": {"value": "gbr"}, "date": "2024", "value": "8"},
                ]
            ),
            True,
            client.Series(
                [5.0, 6.0, 7.0, 8.0],
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("usa", "2024"),
                        ("gbr", "2023"),
                        ("gbr", "2024"),
                    ),
                    names=["country", "date"],
                ),
                name="value",
            ),
            id="multi-country, multi-date",
        ),
        pytest.param(
            fetcher.Result(
                [
                    {"country": {"value": "usa"}, "date": "2023", "value": "5"},
                    {"country": {"value": "usa"}, "date": "2024", "value": "6"},
                ]
            ),
            True,
            client.Series(
                [5.0, 6.0],
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("usa", "2024"),
                    ),
                    names=["country", "date"],
                ),
                name="value",
            ),
            id="one-country, multi-date, keep_levels",
        ),
        pytest.param(
            fetcher.Result(
                [
                    {"country": {"value": "usa"}, "date": "2023", "value": "5"},
                    {"country": {"value": "gbr"}, "date": "2023", "value": "7"},
                ]
            ),
            True,
            client.Series(
                [5.0, 7.0],
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("gbr", "2023"),
                    ),
                    names=["country", "date"],
                ),
                name="value",
            ),
            id="multi-country, one-date, keep_levels",
        ),
        pytest.param(
            fetcher.Result(
                [
                    {"country": {"value": "usa"}, "date": "2023", "value": "5"},
                    {"country": {"value": "usa"}, "date": "2024", "value": "6"},
                ]
            ),
            False,
            client.Series(
                [5.0, 6.0],
                index=pd.Index(("2023", "2024"), name="date"),
                name="value",
            ),
            id="one-country, multi-date, no keep_levels",
        ),
        pytest.param(
            fetcher.Result(
                [
                    {"country": {"value": "usa"}, "date": "2023", "value": "5"},
                    {"country": {"value": "gbr"}, "date": "2023", "value": "7"},
                ]
            ),
            False,
            client.Series(
                [5.0, 7.0],
                index=pd.Index(("usa", "gbr"), name="country"),
                name="value",
            ),
            id="multi-country, one-date, no keep_levels",
        ),
        pytest.param(
            fetcher.Result(
                [
                    {"country": {"value": "usa"}, "date": "2023", "value": "5"},
                ]
            ),
            False,
            client.Series(
                [5.0],
                index=pd.Index(("2023",), name="date"),
                name="value",
            ),
            id="one-country, one-date, no keep_levels",
        ),
    ),
)
def test_get_series(mock_client, response, keep_levels, expected):
    with mock.patch.object(mock_client, "get_data", mock.Mock(return_value=response)):
        got = mock_client.get_series("foo", keep_levels=keep_levels)
        pd.testing.assert_series_equal(got, expected)


def test_get_dataframe_passthrough(mock_client):
    with mock.patch.object(
        mock_client,
        "get_series",
        mock.Mock(
            side_effect=[
                client.Series(
                    [5.0, 6.0, 7.0, 8.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                            ("gbr", "2023"),
                            ("gbr", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 10.0, 11.0, 12.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                            ("gbr", "2023"),
                            ("gbr", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ]
        ),
    ) as mock_get_series:
        kwargs = dict(
            country="usa",
            date="2023",
            freq="Q",
            source="2",
            parse_dates=True,
            keep_levels=True,
            skip_cache=True,
        )

        indicators = {"foo": "bar", "baz": "bat"}
        mock_client.get_dataframe(indicators=indicators, **kwargs)
        for i, indicator in enumerate(indicators):
            assert mock_get_series.mock_calls[i].kwargs == {
                "indicator": indicator,
                **kwargs,
            }


@pytest.mark.parametrize(
    ("results", "indicators", "keep_levels", "expected"),
    (
        pytest.param(
            [
                client.Series(
                    [5.0, 6.0, 7.0, 8.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                            ("gbr", "2023"),
                            ("gbr", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 10.0, 11.0, 12.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                            ("gbr", "2023"),
                            ("gbr", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            False,
            client.DataFrame(
                {
                    "bar": [5.0, 6.0, 7.0, 8.0],
                    "bat": [9.0, 10.0, 11.0, 12.0],
                },
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("usa", "2024"),
                        ("gbr", "2023"),
                        ("gbr", "2024"),
                    ),
                    names=["country", "date"],
                ),
            ),
            id="matching index, multi-country, multi-year",
        ),
        pytest.param(
            [
                client.Series(
                    [5.0, 6.0, 7.0, 8.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                            ("gbr", "2023"),
                            ("gbr", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 10.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            False,
            client.DataFrame(
                {
                    "bar": [5.0, 6.0, 7.0, 8.0],
                    "bat": [9.0, 10.0, None, None],
                },
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("usa", "2024"),
                        ("gbr", "2023"),
                        ("gbr", "2024"),
                    ),
                    names=["country", "date"],
                ),
            ),
            id="overlapping index, multi-country, multi-year",
        ),
        pytest.param(
            [
                client.Series(
                    [7.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(("gbr", "2023"),),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [10.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(("usa", "2024"),),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            False,
            client.DataFrame(
                {
                    "bar": [None, 7.0],
                    "bat": [10.0, None],
                },
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2024"),
                        ("gbr", "2023"),
                    ),
                    names=["country", "date"],
                ),
            ),
            id="disjoint index, multi-country, multi-year",
        ),
        pytest.param(
            [
                client.Series(
                    [5.0, 6.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 10.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            True,
            client.DataFrame(
                {
                    "bar": [5.0, 6.0],
                    "bat": [9.0, 10.0],
                },
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("usa", "2024"),
                    ),
                    names=["country", "date"],
                ),
            ),
            id="One country, keep levels",
        ),
        pytest.param(
            [
                client.Series(
                    [5.0, 7.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("gbr", "2023"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 11.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("gbr", "2023"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            True,
            client.DataFrame(
                {
                    "bar": [5.0, 7.0],
                    "bat": [9.0, 11.0],
                },
                index=pd.MultiIndex.from_tuples(
                    tuples=(
                        ("usa", "2023"),
                        ("gbr", "2023"),
                    ),
                    names=["country", "date"],
                ),
            ),
            id="multi-country, one date, keep levels",
        ),
        pytest.param(
            [
                client.Series(
                    [5.0, 6.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 10.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("usa", "2024"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            False,
            client.DataFrame(
                {
                    "bar": [5.0, 6.0],
                    "bat": [9.0, 10.0],
                },
                index=pd.Index(["2023", "2024"], name="date"),
            ),
            id="One country, no keep levels",
        ),
        pytest.param(
            [
                client.Series(
                    [5.0, 7.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("gbr", "2023"),
                        ),
                        names=["country", "date"],
                    ),
                ),
                client.Series(
                    [9.0, 11.0],
                    index=pd.MultiIndex.from_tuples(
                        tuples=(
                            ("usa", "2023"),
                            ("gbr", "2023"),
                        ),
                        names=["country", "date"],
                    ),
                ),
            ],
            {"foo": "bar", "baz": "bat"},
            False,
            client.DataFrame(
                {
                    "bar": [5.0, 7.0],
                    "bat": [9.0, 11.0],
                },
                index=pd.Index(["usa", "gbr"], name="country"),
            ),
            id="multi-country, one date, no keep levels",
        ),
    ),
)
def test_get_dataframe(mock_client, results, indicators, keep_levels, expected):
    with mock.patch.object(mock_client, "get_series", mock.Mock(side_effect=results)):
        got = mock_client.get_dataframe(indicators=indicators, keep_levels=keep_levels)
        pd.testing.assert_frame_equal(got.loc[expected.index], expected)
