#!/usr/bin/env python3

import datetime

import pytest
import wbdata


class TestSimpleQueries:
    def testGetAllIncomeLevels(self):
        wbdata.get_incomelevel()

    def testOneIncomeLevel(self):
        wbdata.get_incomelevel("HIC")

    def testGetAllLendingTypes(self):
        wbdata.get_lendingtype()

    def testOneLendingType(self):
        wbdata.get_lendingtype("IBD")

    def testGetAllSources(self):
        wbdata.get_source()

    def testOneSource(self):
        wbdata.get_source(31)

    def testGetAllTopics(self):
        wbdata.get_source()

    def testOneTopic(self):
        wbdata.get_source("3")


class TestGetCountry:
    def testAllCountries(self):
        wbdata.get_country()

    def testUSA(self):
        wbdata.get_country(country_id="USA")

    def testHIC(self):
        wbdata.get_country(incomelevel="HIC")

    def testIDB(self):
        wbdata.get_country(lendingtype="IDB")

    def testBadCountry(self):
        with pytest.raises(RuntimeError):
            wbdata.get_country(country_id="Foobar")

    def testBadIncomeLevel(self):
        with pytest.raises(RuntimeError):
            wbdata.get_country(incomelevel="Foobar")

    def testBadLendingType(self):
        with pytest.raises(RuntimeError):
            wbdata.get_country(incomelevel="Foobar")


class TestGetIndicator:
    def testGetAllIndicators(self):
        wbdata.get_indicator()

    def testGetOneIndicator(self):
        wbdata.get_indicator("SP.POP.TOTL")

    def testGetIndicatorBySource(self):
        wbdata.get_indicator(source=1)

    def testGetIndicatorByTopic(self):
        wbdata.get_indicator(topic="1")

    def testGetIndicatorBySourceAndTopic(self):
        with pytest.raises(ValueError):
            wbdata.get_indicator(source="1", topic=1)


class TestGetData:
    def testIndicator(self):
        wbdata.get_data("SP.POP.TOTL")

    def testOneCountry(self):
        wbdata.get_data("SP.POP.TOTL", country="USA")

    def testTwoCountries(self):
        wbdata.get_data("SP.POP.TOTL", country=("chn", "bra"))

    def testDate(self):
        wbdata.get_data(
            "SP.POP.TOTL",
            country="usa",
            data_date=datetime.datetime(2006, 1, 1),
        )

    def testDateRange(self):
        wbdata.get_data(
            "SP.POP.TOTL",
            country="usa",
            data_date=(
                datetime.datetime(2006, 1, 1),
                datetime.datetime(2010, 1, 1),
            ),
        )

    def testConvertDate(self):
        wbdata.get_data("SP.POP.TOTL", country="usa", convert_date=True)

    def testPandas(self):
        wbdata.get_data("SP.POP.TOTL", country="usa", pandas=True)

    def testColumnName(self):
        wbdata.get_data(
            "SP.POP.TOTL", country="usa", pandas=True, column_name="IForget"
        )

    def testSource(self):
        data2 = wbdata.get_data(
            "NY.GDP.MKTP.CD",
            source=2,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2[0]["value"] == 2117039512.19512
        data11 = wbdata.get_data(
            "NY.GDP.MKTP.CD",
            source=11,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11[0]["value"] == 2117008130.0813

    def testLastUpdated(self):
        data = wbdata.get_data("SP.POP.TOTL", country="USA")
        assert isinstance(data.last_updated, datetime.datetime)


class TestSearchFunctions:
    def testSearchCountry(self):
        wbdata.search_countries("United")

    def testSearchIndicators(self):
        wbdata.search_indicators("gdp")


class TestGetSeries:
    indicator = "NY.GDP.MKTP.PP.KD"

    def testOneCountry(self):
        country = "USA"
        series = wbdata.get_series(self.indicator, country=country)
        assert series.index.name == "date"

    def testCountries(self):
        countries = ["GBR", "USA"]
        series = wbdata.get_series(self.indicator, country=countries)
        assert sorted(set(series.index.get_level_values("country"))) == [
            "United Kingdom",
            "United States",
        ]

    def testDate(self):
        data_date = datetime.datetime(2008, 1, 1)
        series = wbdata.get_series(self.indicator, data_date=data_date)
        assert series.index.name == "country"

    def testDateRange(self):
        data_date = (
            datetime.datetime(2008, 1, 1),
            datetime.datetime(2010, 1, 1),
        )
        series = wbdata.get_series(
            self.indicator, data_date=data_date, convert_date=True
        )
        assert min(series.index.get_level_values("date")).year == 2008
        assert max(series.index.get_level_values("date")).year == 2010

    def testConvertDate(self):
        series = wbdata.get_series(self.indicator, convert_date=True)
        assert isinstance(
            series.index.get_level_values("date")[0], datetime.datetime
        )

    def testSource(self):
        data2 = wbdata.get_series(
            "NY.GDP.MKTP.CD",
            source=2,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2.iloc[0] == 2117039512.19512
        data11 = wbdata.get_series(
            "NY.GDP.MKTP.CD",
            source=11,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11.iloc[0] == 2117008130.0813

    def testColumnName(self):
        series = wbdata.get_series(self.indicator, column_name="foo")
        assert series.name == "foo"

    def testLastUpdated(self):
        series = wbdata.get_series(self.indicator)
        assert isinstance(series.last_updated, datetime.datetime)


class TestGetDataframe:
    indicators = {
        "NY.GDP.MKTP.PP.KD": "gdp",
        "NY.GDP.PCAP.PP.KD": "gdppc",
    }

    def testCountries(self):
        countries = ("USA", "GBR")
        wbdata.get_dataframe(self.indicators, country=countries)

    def testDate(self):
        data_date = datetime.datetime(2008, 1, 1)
        wbdata.get_dataframe(self.indicators, data_date=data_date)

    def testDateRange(self):
        data_date = (
            datetime.datetime(2008, 1, 1),
            datetime.datetime(2010, 1, 1),
        )
        wbdata.get_dataframe(self.indicators, data_date=data_date)

    def testConvertDate(self):
        wbdata.get_dataframe(self.indicators, convert_date=True)

    def testColumnName(self):
        df = wbdata.get_dataframe(self.indicators)
        assert tuple(sorted(df.columns)) == ("gdp", "gdppc")

    def testSource(self):
        data2 = wbdata.get_dataframe(
            {"NY.GDP.MKTP.CD": "gdp"},
            source=2,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data2["gdp"].iloc[0] == 2117039512.19512
        data11 = wbdata.get_dataframe(
            {"NY.GDP.MKTP.CD": "gdp"},
            source=11,
            data_date=datetime.datetime(2010, 1, 1),
            country="ERI",
        )
        assert data11["gdp"].iloc[0] == 2117008130.0813

    def testLastUpdated(self):
        df = wbdata.get_dataframe(self.indicators)
        assert isinstance(df.last_updated, dict)
        assert sorted(df.columns) == sorted(df.last_updated.keys())
        assert all(
            isinstance(date, datetime.datetime)
            for date in df.last_updated.values()
        )
