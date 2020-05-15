#!/usr/bin/env python3

import collections
import datetime as dt
import itertools

import pytest
import wbdata as wbd


SimpleCallDefinition = collections.namedtuple(
    "SimpleCallDefinition", ["function", "valid_id", "value"]
)

SimpleCallSpec = collections.namedtuple(
    "SimpleCallSpec", ["function", "result_all", "result_one", "id", "value"]
)

SIMPLE_CALL_DEFINITIONS = [
    SimpleCallDefinition(
        function=wbd.get_country,
        valid_id="USA",  # USA! USA!
        value={
            "id": "USA",
            "iso2Code": "US",
            "name": "United States",
            "region": {"id": "NAC", "iso2code": "XU", "value": "North America"},
            "adminregion": {"id": "", "iso2code": "", "value": ""},
            "incomeLevel": {"id": "HIC", "iso2code": "XD", "value": "High income"},
            "lendingType": {"id": "LNX", "iso2code": "XX", "value": "Not classified"},
            "capitalCity": "Washington D.C.",
            "longitude": "-77.032",
            "latitude": "38.8895",
        },
    ),
    SimpleCallDefinition(
        function=wbd.get_incomelevel,
        valid_id="HIC",
        value={"id": "HIC", "iso2code": "XD", "value": "High income"},
    ),
    SimpleCallDefinition(
        function=wbd.get_lendingtype,
        valid_id="IBD",
        value={"id": "IBD", "iso2code": "XF", "value": "IBRD"},
    ),
    SimpleCallDefinition(
        function=wbd.get_source,
        valid_id="2",
        value={
            "id": "2",
            "name": "World Development Indicators",
            "code": "WDI",
            "description": "",
            "url": "",
            "dataavailability": "Y",
            "metadataavailability": "Y",
            "concepts": "3",
        },
    ),
    SimpleCallDefinition(
        function=wbd.get_topic,
        valid_id="3",
        value={
            "id": "3",
            "value": "Economy & Growth",
            "sourceNote": (
                "Economic growth is central to economic development. When "
                "national income grows, real people benefit. While there is "
                "no known formula for stimulating economic growth, data can "
                "help policy-makers better understand their countries' "
                "economic situations and guide any work toward improvement. "
                "Data here covers measures of economic growth, such as gross "
                "domestic product (GDP) and gross national income (GNI). It "
                "also includes indicators representing factors known to be "
                "relevant to economic growth, such as capital stock, "
                "employment, investment, savings, consumption, government "
                "spending, imports, and exports."
            ),
        },
    ),
    SimpleCallDefinition(
        function=wbd.get_indicator,
        valid_id="SP.POP.TOTL",
        value={
            "id": "SP.POP.TOTL",
            "name": "Population, total",
            "unit": "",
            "source": {"id": "2", "value": "World Development Indicators"},
            "sourceNote": (
                "Total population is based on the de facto definition of "
                "population, which counts all residents regardless of legal "
                "status or citizenship. The values shown are midyear "
                "estimates."
            ),
            "sourceOrganization": (
                "(1) United Nations Population Division. World Population "
                "Prospects: 2019 Revision. (2) Census reports and other "
                "statistical publications from national statistical offices, "
                "(3) Eurostat: Demographic Statistics, (4) United Nations "
                "Statistical Division. Population and Vital Statistics "
                "Reprot (various years), (5) U.S. Census Bureau: "
                "International Database, and (6) Secretariat of the Pacific "
                "Community: Statistics and Demography Programme."
            ),
            "topics": [
                {"id": "19", "value": "Climate Change"},
                {"id": "8", "value": "Health "},
            ],
        },
    ),
]


@pytest.fixture(params=SIMPLE_CALL_DEFINITIONS, scope="class")
def simple_call_spec(request):
    return SimpleCallSpec(
        function=request.param.function,
        result_all=request.param.function(),
        result_one=request.param.function(request.param.valid_id),
        id=request.param.valid_id,
        value=request.param.value,
    )


class TestSimpleQueries:
    """
    Test that results of simple queries are close to what we expect
    """

    def test_simple_all_type(self, simple_call_spec):
        assert isinstance(simple_call_spec.result_all, wbd.api.WBSearchResult)

    def test_simple_all_len(self, simple_call_spec):
        assert len(simple_call_spec.result_all) > 1

    def test_simple_all_content(self, simple_call_spec):
        expected = []
        for val in simple_call_spec.result_all:
            try:
                del val["lastupdated"]
            except KeyError:
                pass
            expected.append(val)
        assert simple_call_spec.value in expected

    def test_simple_one_type(self, simple_call_spec):
        assert isinstance(simple_call_spec.result_one, wbd.api.WBSearchResult)

    def test_simple_one_len(self, simple_call_spec):
        assert len(simple_call_spec.result_one) == 1

    def test_simple_one_content(self, simple_call_spec):
        got = simple_call_spec.result_one[0]
        try:
            del got["lastupdated"]
        except KeyError:
            pass
        assert simple_call_spec.result_one[0] == simple_call_spec.value

    def test_simple_bad_call(self, simple_call_spec):
        with pytest.raises(RuntimeError):
            simple_call_spec.function("Ain'tNotAThing")


class TestGetIndicator:
    """Extra tests for Get Indicator"""

    def testGetIndicatorBySource(self):
        indicators = wbd.get_indicator(source=1)
        assert all(i["source"]["id"] == "1" for i in indicators)

    def testGetIndicatorByTopic(self):
        indicators = wbd.get_indicator(topic=1)
        assert all(any(t["id"] == "1" for t in i["topics"]) for i in indicators)

    def testGetIndicatorBySourceAndTopicFails(self):
        with pytest.raises(ValueError):
            wbd.get_indicator(source="1", topic=1)


SearchDefinition = collections.namedtuple(
    "SearchDefinition",
    ["function", "query", "value", "facets", "facet_matches", "facet_mismatches"],
)

SearchData = collections.namedtuple(
    "SearchData",
    [
        "function",
        "query",
        "value",
        "facets",
        "results",
        "results_facet_matches",
        "results_facet_mismatches",
    ],
)

search_definitions = [
    SearchDefinition(
        function=wbd.search_countries,
        query="United",
        value={
            "id": "USA",
            "iso2Code": "US",
            "name": "United States",
            "region": {"id": "NAC", "iso2code": "XU", "value": "North America"},
            "adminregion": {"id": "", "iso2code": "", "value": ""},
            "incomeLevel": {"id": "HIC", "iso2code": "XD", "value": "High income"},
            "lendingType": {"id": "LNX", "iso2code": "XX", "value": "Not classified"},
            "capitalCity": "Washington D.C.",
            "longitude": "-77.032",
            "latitude": "38.8895",
        },
        facets=["incomelevel", "lendingtype"],
        facet_matches=["HIC", "LNX"],
        facet_mismatches=["LIC", "IDX"],
    )
]


GetDataSpec = collections.namedtuple(
    "GetDataSpec",
    [
        "result",
        "country",
        "data_date",
        "source",
        "convert_date",
        "expected_country",
        "expected_date",
        "expected_value",
    ],
)


@pytest.fixture(params=search_definitions, scope="class")
def search_data(request):
    return SearchData(
        function=request.param.function,
        query=request.param.query,
        value=request.param.value,
        facets=request.param.facets,
        results=request.param.function(request.param.query),
        results_facet_matches=[
            request.param.function(request.param.query, **{facet: value})
            for facet, value in zip(request.param.facets, request.param.facet_matches)
        ],
        results_facet_mismatches=[
            request.param.function(request.param.query, **{facet: value})
            for facet, value in zip(
                request.param.facets, request.param.facet_mismatches
            )
        ],
    )


class TestSearchFunctions:
    def test_search_return_type(self, search_data):
        assert isinstance(search_data.results, wbd.api.WBSearchResult)

    def test_facet_return_type(self, search_data):
        for results in (
            search_data.results_facet_matches + search_data.results_facet_mismatches
        ):
            assert isinstance(results, wbd.api.WBSearchResult)

    def test_plain_search(self, search_data):
        assert search_data.value in search_data.results

    def test_matched_faceted_searches(self, search_data):
        for results in search_data.results_facet_matches:
            assert search_data.value in results

    def test_mismatched_faceted_searches(self, search_data):
        for results in search_data.results_facet_mismatches:
            assert search_data.value not in results


COUNTRY_NAMES = {
    "ERI": "Eritrea",
    "GNQ": "Equatorial Guinea",
}

common_data_facets = [
    ["all", "ERI", ["ERI", "GNQ"]],
    [
        None,
        dt.datetime(2010, 1, 1),
        [dt.datetime(2010, 1, 1), dt.datetime(2011, 1, 1)],
    ],
    [None, "2", "11"],
    [False, True],
]
get_data_defs = itertools.product(*common_data_facets)


@pytest.fixture(params=get_data_defs, scope="class")
def get_data_spec(request):
    country, data_date, source, convert_date = request.param
    return GetDataSpec(
        result=wbd.get_data(
            "NY.GDP.MKTP.CD",
            country=country,
            data_date=data_date,
            source=source,
            convert_date=convert_date,
        ),
        country=country,
        data_date=data_date,
        source=source,
        convert_date=convert_date,
        expected_country="Eritrea",
        expected_date=dt.datetime(2010, 1, 1) if convert_date else "2010",
        expected_value={"2": 2117039512.19512, "11": 2117008130.0813}[source or "2"],
    )


class TestGetData:
    def test_result_type(self, get_data_spec):
        assert isinstance(get_data_spec.result, wbd.fetcher.WBResults)

    def test_country(self, get_data_spec):
        if get_data_spec.country == "all":
            return
        expected = (
            {get_data_spec.country}
            if isinstance(get_data_spec.country, str)
            else set(get_data_spec.country)
        )
        # This is a little complicated because the API returns the iso3 id
        # in different places from different sources (which is insane)
        got = set(
            [
                i["countryiso3code"] if i["countryiso3code"] else i["country"]["id"]
                for i in get_data_spec.result
            ]
        )
        try:
            assert got == expected
        except AssertionError:
            raise

    #  Tests both string and converted dates
    def test_data_date(self, get_data_spec):
        if get_data_spec.data_date is None:
            return
        expected = (
            set(get_data_spec.data_date)
            if isinstance(get_data_spec.data_date, collections.Sequence)
            else {get_data_spec.data_date}
        )
        if not get_data_spec.convert_date:
            expected = {date.strftime("%Y") for date in expected}

        got = {i["date"] for i in get_data_spec.result}
        assert got == expected

    # Tests source and correct value
    def test_content(self, get_data_spec):
        got = next(
            datum["value"]
            for datum in get_data_spec.result
            if datum["country"]["value"] == get_data_spec.expected_country
            and datum["date"] == get_data_spec.expected_date
        )
        assert got == get_data_spec.expected_value

    def testLastUpdated(self, get_data_spec):
        assert isinstance(get_data_spec.result.last_updated, dt.datetime)

    def testMonthlyFreq(self):
        got = wbd.get_data(
            "DPANUSSPB", country="bra", data_date=dt.datetime(2012, 1, 1), freq="M"
        )[0]["value"]
        assert got == 1.78886363636

    def testQuarterlyFreq(self):
        got = wbd.get_data(
            "DP.DOD.DECD.CR.BC.CD",
            country="chl",
            data_date=dt.datetime(2013, 1, 1),
            freq="Q",
        )[0]["value"]
        assert got == 31049138725.7794


series_data_facets = tuple(
    itertools.product(*(common_data_facets + [["value", "other"], [False, True]]))
)


GetSeriesSpec = collections.namedtuple(
    "GetSeriesSpec",
    [
        "result",
        "country",
        "data_date",
        "source",
        "convert_date",
        "column_name",
        "keep_levels",
        "expected_country",
        "expected_date",
        "expected_value",
        "country_in_index",
        "date_in_index",
    ],
)


@pytest.fixture(params=series_data_facets, scope="class")
def get_series_spec(request):
    (
        country,
        data_date,
        source,
        convert_date,
        column_name,
        keep_levels,
    ) = request.param
    return GetSeriesSpec(
        result=wbd.get_series(
            "NY.GDP.MKTP.CD",
            country=country,
            data_date=data_date,
            source=source,
            convert_date=convert_date,
            column_name=column_name,
            keep_levels=keep_levels,
        ),
        country=country,
        data_date=data_date,
        source=source,
        convert_date=convert_date,
        column_name=column_name,
        keep_levels=keep_levels,
        expected_country="Eritrea",
        expected_date=dt.datetime(2010, 1, 1) if convert_date else "2010",
        expected_value={"2": 2117039512.19512, "11": 2117008130.0813}[source or "2"],
        country_in_index=(
            country == "all" or not isinstance(country, str) or keep_levels
        ),
        date_in_index=(not isinstance(data_date, dt.datetime) or keep_levels),
    )


class TestGetSeries:
    def test_index_labels(self, get_series_spec):
        index = get_series_spec.result.index
        if get_series_spec.country_in_index:
            if get_series_spec.date_in_index:
                assert index.names == ["country", "date"]
            else:
                assert index.name == "country"
        else:
            assert index.name == "date"

    def test_country(self, get_series_spec):
        if not get_series_spec.country_in_index:
            return
        got = sorted(get_series_spec.result.index.unique(level="country"))

        if get_series_spec.country == "all":
            assert len(got) > 2
        elif isinstance(get_series_spec.country, str):
            assert len(got) == 1
            assert got[0] == COUNTRY_NAMES[get_series_spec.country]
        else:
            assert got == sorted(
                COUNTRY_NAMES[country] for country in get_series_spec.country
            )

    def test_date(self, get_series_spec):
        if not get_series_spec.date_in_index:
            return
        got = sorted(get_series_spec.result.index.unique(level="date"))
        if get_series_spec.data_date is None:
            assert len(got) > 2
        elif isinstance(get_series_spec.data_date, collections.Sequence):
            assert got == sorted(
                date if get_series_spec.convert_date else date.strftime("%Y")
                for date in get_series_spec.data_date
            )
        else:
            assert len(got) == 1
            assert got[0] == (
                get_series_spec.data_date
                if get_series_spec.convert_date
                else get_series_spec.data_date.strftime("%Y")
            )

    def test_column_name(self, get_series_spec):
        assert get_series_spec.result.name == get_series_spec.column_name

    def test_value(self, get_series_spec):
        if get_series_spec.country_in_index:
            if get_series_spec.date_in_index:
                index_loc = (
                    get_series_spec.expected_country,
                    get_series_spec.expected_date,
                )
            else:
                index_loc = get_series_spec.expected_country
        else:
            index_loc = get_series_spec.expected_date

        assert get_series_spec.result[index_loc] == get_series_spec.expected_value

    def test_last_updated(self, get_series_spec):
        assert isinstance(get_series_spec.result.last_updated, dt.datetime)

    def test_bad_value(self):
        with pytest.raises(RuntimeError):
            wbd.get_series("AintNotAThing")


GetDataFrameSpec = collections.namedtuple(
    "GetDataFrameSpec",
    [
        "result",
        "country",
        "data_date",
        "source",
        "convert_date",
        "column_names",
        "keep_levels",
        "expected_country",
        "expected_date",
        "expected_column",
        "expected_value",
        "country_in_index",
        "date_in_index",
    ],
)


@pytest.fixture(params=series_data_facets, scope="class")
def get_dataframe_spec(request):
    (
        country,
        data_date,
        source,
        convert_date,
        column_name,
        keep_levels,
    ) = request.param
    return GetDataFrameSpec(
        result=wbd.get_dataframe(
            {"NY.GDP.MKTP.CD": column_name, "NY.GDP.MKTP.PP.CD": "ppp"},
            country=country,
            data_date=data_date,
            source=source,
            convert_date=convert_date,
            keep_levels=keep_levels,
        ),
        country=country,
        data_date=data_date,
        source=source,
        convert_date=convert_date,
        column_names=[column_name, "ppp"],
        keep_levels=keep_levels,
        expected_country="Eritrea",
        expected_date=dt.datetime(2010, 1, 1) if convert_date else "2010",
        expected_column=column_name,
        expected_value={"2": 2117039512.19512, "11": 2117008130.0813}[source or "2"],
        country_in_index=(
            country == "all" or not isinstance(country, str) or keep_levels
        ),
        date_in_index=(not isinstance(data_date, dt.datetime) or keep_levels),
    )


class TestGetDataFrame:
    def test_index_labels(self, get_dataframe_spec):
        index = get_dataframe_spec.result.index
        if get_dataframe_spec.country_in_index:
            if get_dataframe_spec.date_in_index:
                assert index.names == ["country", "date"]
            else:
                assert index.name == "country"
        else:
            assert index.name == "date"

    def test_country(self, get_dataframe_spec):
        if not get_dataframe_spec.country_in_index:
            return
        got = sorted(get_dataframe_spec.result.index.unique(level="country"))

        if get_dataframe_spec.country == "all":
            assert len(got) > 2
        elif isinstance(get_dataframe_spec.country, str):
            assert len(got) == 1
            assert got[0] == COUNTRY_NAMES[get_dataframe_spec.country]
        else:
            assert got == sorted(
                COUNTRY_NAMES[country] for country in get_dataframe_spec.country
            )

    def test_date(self, get_dataframe_spec):
        if not get_dataframe_spec.date_in_index:
            return
        got = sorted(get_dataframe_spec.result.index.unique(level="date"))
        if get_dataframe_spec.data_date is None:
            assert len(got) > 2
        elif isinstance(get_dataframe_spec.data_date, collections.Sequence):
            assert got == sorted(
                date if get_dataframe_spec.convert_date else date.strftime("%Y")
                for date in get_dataframe_spec.data_date
            )
        else:
            assert len(got) == 1
            assert got[0] == (
                get_dataframe_spec.data_date
                if get_dataframe_spec.convert_date
                else get_dataframe_spec.data_date.strftime("%Y")
            )

    def test_column_name(self, get_dataframe_spec):
        assert (
            get_dataframe_spec.result.columns.tolist()
            == get_dataframe_spec.column_names
        )

    def test_value(self, get_dataframe_spec):
        if get_dataframe_spec.country_in_index:
            if get_dataframe_spec.date_in_index:
                index_loc = (
                    get_dataframe_spec.expected_country,
                    get_dataframe_spec.expected_date,
                )
            else:
                index_loc = get_dataframe_spec.expected_country
        else:
            index_loc = get_dataframe_spec.expected_date

        assert (
            get_dataframe_spec.result[get_dataframe_spec.expected_column][index_loc]
            == get_dataframe_spec.expected_value
        )

    def test_last_updated(self, get_dataframe_spec):
        assert all(
            isinstance(value, dt.datetime)
            for value in get_dataframe_spec.result.last_updated.values()
        )

    def test_bad_value(self):
        with pytest.raises(RuntimeError):
            wbd.get_dataframe({"AintNotAThing": "bad value"})
