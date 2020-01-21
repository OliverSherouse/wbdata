#!/usr/bin/env python3

import collections
import datetime as dt
import itertools

import pytest
import wbdata as wbd


SimpleCallDefinition = collections.namedtuple(
    "SimpleCallDefinition", ["function", "valid_id", "value"]
)

SimpleCallData = collections.namedtuple(
    "SimpleCallData", ["function", "result_all", "result_one", "id", "value"]
)

SIMPLE_CALL_DEFINITIONS = [
    SimpleCallDefinition(
        function=wbd.get_country,
        valid_id="USA",  # USA! USA!
        value={
            "id": "USA",
            "iso2Code": "US",
            "name": "United States",
            "region": {
                "id": "NAC",
                "iso2code": "XU",
                "value": "North America",
            },
            "adminregion": {"id": "", "iso2code": "", "value": ""},
            "incomeLevel": {
                "id": "HIC",
                "iso2code": "XD",
                "value": "High income",
            },
            "lendingType": {
                "id": "LNX",
                "iso2code": "XX",
                "value": "Not classified",
            },
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
            "lastupdated": "2019-12-20",
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


@pytest.fixture(params=SIMPLE_CALL_DEFINITIONS)
def simple_call_data(request):
    return SimpleCallData(
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

    def test_simple_all_type(self, simple_call_data):
        assert isinstance(simple_call_data.result_all, wbd.api.WBSearchResult)

    def test_simple_all_len(self, simple_call_data):
        assert len(simple_call_data.result_all) > 1

    def test_simple_all_content(self, simple_call_data):
        assert simple_call_data.value in simple_call_data.result_all

    def test_simple_one_type(self, simple_call_data):
        assert isinstance(simple_call_data.result_one, wbd.api.WBSearchResult)

    def test_simple_one_len(self, simple_call_data):
        assert len(simple_call_data.result_one) == 1

    def test_simple_one_content(self, simple_call_data):
        assert simple_call_data.result_one[0] == simple_call_data.value

    def test_simple_bad_call(self, simple_call_data):
        with pytest.raises(RuntimeError):
            simple_call_data.function("Ain'tNotAThing")


class TestGetIndicator:
    """Extra tests for Get Indicator"""

    def testGetIndicatorBySource(self):
        indicators = wbd.get_indicator(source=1)
        assert all(i["source"]["id"] == "1" for i in indicators)

    def testGetIndicatorByTopic(self):
        indicators = wbd.get_indicator(topic=1)
        assert all(
            any(t["id"] == "1" for t in i["topics"]) for i in indicators
        )

    def testGetIndicatorBySourceAndTopicFails(self):
        with pytest.raises(ValueError):
            wbd.get_indicator(source="1", topic=1)


SearchDefinition = collections.namedtuple(
    "SearchDefinition",
    [
        "function",
        "query",
        "value",
        "facets",
        "facet_matches",
        "facet_mismatches",
    ],
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
            "region": {
                "id": "NAC",
                "iso2code": "XU",
                "value": "North America",
            },
            "adminregion": {"id": "", "iso2code": "", "value": ""},
            "incomeLevel": {
                "id": "HIC",
                "iso2code": "XD",
                "value": "High income",
            },
            "lendingType": {
                "id": "LNX",
                "iso2code": "XX",
                "value": "Not classified",
            },
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


@pytest.fixture(params=search_definitions)
def search_data(request):
    return SearchData(
        function=request.param.function,
        query=request.param.query,
        value=request.param.value,
        facets=request.param.facets,
        results=request.param.function(request.param.query),
        results_facet_matches=[
            request.param.function(request.param.query, **{facet: value})
            for facet, value in zip(
                request.param.facets, request.param.facet_matches
            )
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
            search_data.results_facet_matches
            + search_data.results_facet_mismatches
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


get_data_defs = itertools.product(
    ["all", "ERI", ["ERI", "GNQ"]],
    [
        None,
        dt.datetime(2010, 1, 1),
        [dt.datetime(2010, 1, 1), dt.datetime(2011, 1, 1)],
    ],
    [None, "2", "11"],
    [False, True],
)


@pytest.fixture(params=get_data_defs)
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
        expected_value={"2": 2117039512.19512, "11": 2117008130.0813},
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
                i["countryiso3code"]
                if i["countryiso3code"]
                else i["country"]["id"]
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
        expected = get_data_spec.expected_value[get_data_spec.source or "2"]
        got = next(
            datum["value"]
            for datum in get_data_spec.result
            if datum["country"]["value"] == get_data_spec.expected_country
            and datum["date"] == get_data_spec.expected_date
        )
        assert got == expected

    def testLastUpdated(self, get_data_spec):
        assert isinstance(get_data_spec.result.last_updated, dt.datetime)


class TestGetSeries:
    indicator = "NY.GDP.MKTP.PP.KD"

    def testOneCountry(self):
        country = "USA"
        series = wbd.get_series(self.indicator, country=country)
        assert series.index.name == "date"

    def testCountries(self):
        countries = ["GBR", "USA"]
        series = wbd.get_series(self.indicator, country=countries)
        assert sorted(set(series.index.get_level_values("country"))) == [
            "United Kingdom",
            "United States",
        ]

    def testDate(self):
        data_date = dt.datetime(2008, 1, 1)
        series = wbd.get_series(self.indicator, data_date=data_date)
        assert series.index.name == "country"

    def testDateRange(self):
        data_date = (
            dt.datetime(2008, 1, 1),
            dt.datetime(2010, 1, 1),
        )
        series = wbd.get_series(
            self.indicator, data_date=data_date, convert_date=True
        )
        assert min(series.index.get_level_values("date")).year == 2008
        assert max(series.index.get_level_values("date")).year == 2010

    def testConvertDate(self):
        series = wbd.get_series(self.indicator, convert_date=True)
        assert isinstance(
            series.index.get_level_values("date")[0], dt.datetime
        )

    def testSource(self):
        data2 = wbd.get_series(
            "NY.GDP.MKTP.CD",
            source=2,
            data_date=dt.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2.iloc[0] == 2117039512.19512
        data11 = wbd.get_series(
            "NY.GDP.MKTP.CD",
            source=11,
            data_date=dt.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11.iloc[0] == 2117008130.0813

    def testColumnName(self):
        series = wbd.get_series(self.indicator, column_name="foo")
        assert series.name == "foo"

    def testLastUpdated(self):
        series = wbd.get_series(self.indicator)
        assert isinstance(series.last_updated, dt.datetime)


class TestGetDataframe:
    indicators = {
        "NY.GDP.MKTP.PP.KD": "gdp",
        "NY.GDP.PCAP.PP.KD": "gdppc",
    }

    def testCountries(self):
        countries = ("USA", "GBR")
        wbd.get_dataframe(self.indicators, country=countries)

    def testDate(self):
        data_date = dt.datetime(2008, 1, 1)
        wbd.get_dataframe(self.indicators, data_date=data_date)

    def testDateRange(self):
        data_date = (
            dt.datetime(2008, 1, 1),
            dt.datetime(2010, 1, 1),
        )
        wbd.get_dataframe(self.indicators, data_date=data_date)

    def testConvertDate(self):
        wbd.get_dataframe(self.indicators, convert_date=True)

    def testColumnName(self):
        df = wbd.get_dataframe(self.indicators)
        assert tuple(sorted(df.columns)) == ("gdp", "gdppc")

    def testSource(self):
        data2 = wbd.get_dataframe(
            {"NY.GDP.MKTP.CD": "gdp"},
            source=2,
            data_date=dt.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2["gdp"].iloc[0] == 2117039512.19512
        data11 = wbd.get_dataframe(
            {"NY.GDP.MKTP.CD": "gdp"},
            source=11,
            data_date=dt.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11["gdp"].iloc[0] == 2117008130.0813

    def testLastUpdated(self):
        df = wbd.get_dataframe(self.indicators)
        assert isinstance(df.last_updated, dict)
        assert sorted(df.columns) == sorted(df.last_updated.keys())
        assert all(
            isinstance(date, dt.datetime) for date in df.last_updated.values()
        )
