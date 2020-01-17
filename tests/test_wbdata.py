#!/usr/bin/env python3

import datetime

import pytest
import wbdata as wbd


@pytest.fixture
def incomelevels():
    return wbd.get_incomelevel()


@pytest.fixture
def one_incomelevel():
    return wbd.get_incomelevel("HIC")


@pytest.fixture
def lendingtypes():
    return wbd.get_lendingtype()


@pytest.fixture
def one_lendingtype():
    return wbd.get_lendingtype("IBD")


@pytest.fixture
def sources():
    return wbd.get_source()


@pytest.fixture
def one_source():
    return wbd.get_source(2)


@pytest.fixture
def topics():
    return wbd.get_topic()


@pytest.fixture
def one_topic():
    return wbd.get_topic(3)


class TestSimpleQueries:
    """
    Test that results of simple queries are close to what we expect
    """

    def test_incomelevels_type(self, incomelevels):
        assert isinstance(incomelevels, wbd.api.WBSearchResult)

    def test_incomelevels_len(self, incomelevels):
        assert len(incomelevels) > 1

    def test_incomelevels_content(self, incomelevels):
        assert any(i["id"] == "HIC" for i in incomelevels)

    def test_one_incomelevel_type(self, one_incomelevel):
        assert isinstance(one_incomelevel, wbd.api.WBSearchResult)

    def test_one_incomelevel_len(self, one_incomelevel):
        assert len(one_incomelevel) == 1

    def test_one_incomelevel_content(self, one_incomelevel):
        assert one_incomelevel[0] == {
            "id": "HIC",
            "iso2code": "XD",
            "value": "High income",
        }

    def test_lendingtypes_type(self, lendingtypes):
        assert isinstance(lendingtypes, wbd.api.WBSearchResult)

    def test_lendingtypes_len(self, lendingtypes):
        assert len(lendingtypes) > 1

    def test_lendingtypes_content(self, lendingtypes):
        assert any(i["id"] == "IBD" for i in lendingtypes)

    def test_one_lendingtype_type(self, one_lendingtype):
        assert isinstance(one_lendingtype, wbd.api.WBSearchResult)

    def test_one_lendingtype_len(self, one_lendingtype):
        assert len(one_lendingtype) == 1

    def test_one_lendingtype_content(self, one_lendingtype):
        assert one_lendingtype[0] == {
            "id": "IBD",
            "iso2code": "XF",
            "value": "IBRD",
        }

    def test_sources_type(self, sources):
        assert isinstance(sources, wbd.api.WBSearchResult)

    def test_sources_len(self, sources):
        assert len(sources) > 1

    def test_sources_content(self, sources):
        assert any(i["id"] == "2" for i in sources)

    def test_one_source_type(self, one_source):
        assert isinstance(one_source, wbd.api.WBSearchResult)

    def test_one_source_len(self, one_source):
        assert len(one_source) == 1

    def test_one_source_content(self, one_source):
        assert one_source[0] == {
            "id": "2",
            "lastupdated": "2019-12-20",
            "name": "World Development Indicators",
            "code": "WDI",
            "description": "",
            "url": "",
            "dataavailability": "Y",
            "metadataavailability": "Y",
            "concepts": "3",
        }

    def test_topics_type(self, topics):
        assert isinstance(topics, wbd.api.WBSearchResult)

    def test_topics_len(self, topics):
        assert len(topics) > 1

    def test_topics_content(self, topics):
        assert any(i["id"] == "3" for i in topics)

    def test_one_topic_type(self, one_topic):
        assert isinstance(one_topic, wbd.api.WBSearchResult)

    def test_one_topic_len(self, one_topic):
        assert len(one_topic) == 1

    def test_one_topic_content(self, one_topic):
        assert one_topic[0] == {
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
        }


class TestGetCountry:
    def testAllCountries(self):
        wbd.get_country()

    def testUSA(self):
        wbd.get_country(country_id="USA")

    def testHIC(self):
        wbd.get_country(incomelevel="HIC")

    def testIDB(self):
        wbd.get_country(lendingtype="IDB")

    def testBadCountry(self):
        with pytest.raises(RuntimeError):
            wbd.get_country(country_id="Foobar")

    def testBadIncomeLevel(self):
        with pytest.raises(RuntimeError):
            wbd.get_country(incomelevel="Foobar")

    def testBadLendingType(self):
        with pytest.raises(RuntimeError):
            wbd.get_country(incomelevel="Foobar")


class TestGetIndicator:
    def testGetAllIndicators(self):
        wbd.get_indicator()

    def testGetOneIndicator(self):
        wbd.get_indicator("SP.POP.TOTL")

    def testGetIndicatorBySource(self):
        wbd.get_indicator(source=1)

    def testGetIndicatorByTopic(self):
        wbd.get_indicator(topic="1")

    def testGetIndicatorBySourceAndTopic(self):
        with pytest.raises(ValueError):
            wbd.get_indicator(source="1", topic=1)


class TestGetData:
    def testIndicator(self):
        wbd.get_data("SP.POP.TOTL")

    def testOneCountry(self):
        wbd.get_data("SP.POP.TOTL", country="USA")

    def testTwoCountries(self):
        wbd.get_data("SP.POP.TOTL", country=("chn", "bra"))

    def testDate(self):
        wbd.get_data(
            "SP.POP.TOTL",
            country="usa",
            data_date=datetime.datetime(2006, 1, 1),
        )

    def testDateRange(self):
        wbd.get_data(
            "SP.POP.TOTL",
            country="usa",
            data_date=(
                datetime.datetime(2006, 1, 1),
                datetime.datetime(2010, 1, 1),
            ),
        )

    def testConvertDate(self):
        wbd.get_data("SP.POP.TOTL", country="usa", convert_date=True)

    def testPandas(self):
        wbd.get_data("SP.POP.TOTL", country="usa", pandas=True)

    def testColumnName(self):
        wbd.get_data(
            "SP.POP.TOTL", country="usa", pandas=True, column_name="IForget"
        )

    def testSource(self):
        data2 = wbd.get_data(
            "NY.GDP.MKTP.CD",
            source=2,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2[0]["value"] == 2117039512.19512
        data11 = wbd.get_data(
            "NY.GDP.MKTP.CD",
            source=11,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11[0]["value"] == 2117008130.0813

    def testLastUpdated(self):
        data = wbd.get_data("SP.POP.TOTL", country="USA")
        assert isinstance(data.last_updated, datetime.datetime)


class TestSearchFunctions:
    def testSearchCountry(self):
        wbd.search_countries("United")

    def testSearchIndicators(self):
        wbd.search_indicators("gdp")


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
        data_date = datetime.datetime(2008, 1, 1)
        series = wbd.get_series(self.indicator, data_date=data_date)
        assert series.index.name == "country"

    def testDateRange(self):
        data_date = (
            datetime.datetime(2008, 1, 1),
            datetime.datetime(2010, 1, 1),
        )
        series = wbd.get_series(
            self.indicator, data_date=data_date, convert_date=True
        )
        assert min(series.index.get_level_values("date")).year == 2008
        assert max(series.index.get_level_values("date")).year == 2010

    def testConvertDate(self):
        series = wbd.get_series(self.indicator, convert_date=True)
        assert isinstance(
            series.index.get_level_values("date")[0], datetime.datetime
        )

    def testSource(self):
        data2 = wbd.get_series(
            "NY.GDP.MKTP.CD",
            source=2,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2.iloc[0] == 2117039512.19512
        data11 = wbd.get_series(
            "NY.GDP.MKTP.CD",
            source=11,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11.iloc[0] == 2117008130.0813

    def testColumnName(self):
        series = wbd.get_series(self.indicator, column_name="foo")
        assert series.name == "foo"

    def testLastUpdated(self):
        series = wbd.get_series(self.indicator)
        assert isinstance(series.last_updated, datetime.datetime)


class TestGetDataframe:
    indicators = {
        "NY.GDP.MKTP.PP.KD": "gdp",
        "NY.GDP.PCAP.PP.KD": "gdppc",
    }

    def testCountries(self):
        countries = ("USA", "GBR")
        wbd.get_dataframe(self.indicators, country=countries)

    def testDate(self):
        data_date = datetime.datetime(2008, 1, 1)
        wbd.get_dataframe(self.indicators, data_date=data_date)

    def testDateRange(self):
        data_date = (
            datetime.datetime(2008, 1, 1),
            datetime.datetime(2010, 1, 1),
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
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2["gdp"].iloc[0] == 2117039512.19512
        data11 = wbd.get_dataframe(
            {"NY.GDP.MKTP.CD": "gdp"},
            source=11,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11["gdp"].iloc[0] == 2117008130.0813

    def testLastUpdated(self):
        df = wbd.get_dataframe(self.indicators)
        assert isinstance(df.last_updated, dict)
        assert sorted(df.columns) == sorted(df.last_updated.keys())
        assert all(
            isinstance(date, datetime.datetime)
            for date in df.last_updated.values()
        )
