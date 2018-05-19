#!/usr/bin/env python
from __future__ import (
    print_function, division, absolute_import, unicode_literals
)


import datetime
import unittest
import os.path
import sys

sys.path.append(
    os.path.normpath(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            '..',
        )
    )
)

print(sys.path[-1])

import wbdata


class TestSimpleQueries(unittest.TestCase):
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


class TestGetCountry(unittest.TestCase):
    def testAllCountries(self):
        wbdata.get_country()

    def testUSA(self):
        wbdata.get_country(country_id="USA")

    def testHIC(self):
        wbdata.get_country(incomelevel="HIC")

    def testIDB(self):
        wbdata.get_country(lendingtype="IDB")

    @unittest.expectedFailure
    def testBadCountry(self):
        wbdata.get_country(country_id="Foobar")

    @unittest.expectedFailure
    def testBadIncomeLevel(self):
        wbdata.get_country(incomelevel="Foobar")

    @unittest.expectedFailure
    def testBadLendingType(self):
        wbdata.get_country(incomelevel="Foobar")


class TestGetIndicator(unittest.TestCase):
    def testGetAllIndicators(self):
        wbdata.get_indicator()

    def testGetOneIndicator(self):
        wbdata.get_indicator("SP.POP.TOTL")

    def testGetIndicatorBySource(self):
        wbdata.get_indicator(source=1)

    def testGetIndicatorByTopic(self):
        wbdata.get_indicator(topic="1")

    @unittest.expectedFailure
    def testGetIndicatorBySourceAndTopic(self):
        wbdata.get_indicator(source="1", topic=1)


class TestGetData(unittest.TestCase):
    def testIndicator(self):
        wbdata.get_data("SP.POP.TOTL")

    def testOneCountry(self):
        wbdata.get_data("SP.POP.TOTL", country="USA")

    def testTwoCountries(self):
        wbdata.get_data("SP.POP.TOTL", country=("chn", "bra"))

    def testDate(self):
        wbdata.get_data("SP.POP.TOTL", country="usa",
                        data_date=datetime.datetime(2006, 1, 1))

    def testDateRange(self):
        wbdata.get_data("SP.POP.TOTL", country="usa",
                        data_date=(datetime.datetime(2006, 1, 1),
                                   datetime.datetime(2010, 1, 1)))

    def testConvertDate(self):
        wbdata.get_data("SP.POP.TOTL", country="usa", convert_date=True)

    def testPandas(self):
        wbdata.get_data("SP.POP.TOTL", country="usa", pandas=True)

    def testColumnName(self):
        wbdata.get_data("SP.POP.TOTL", country="usa", pandas=True,
                        column_name="IForget")


class TestSearchFunctions(unittest.TestCase):
    def testSearchCountry(self):
        wbdata.search_countries("United")

    def testSearchIndicators(self):
        wbdata.search_indicators("gdp")


class TestGetSeries(unittest.TestCase):
    def setUp(self):
        self.indicator = "NY.GDP.MKTP.PP.KD"

    def testOneCountry(self):
        country = "USA"
        series = wbdata.get_series(self.indicator, country=country)
        assert series.index.name == 'date'

    def testCountries(self):
        countries = ['GBR', 'USA']
        series = wbdata.get_series(self.indicator, country=countries)
        assert (
            sorted(set(series.index.get_level_values('country'))) ==
            ['United Kingdom', 'United States']
        )

    def testDate(self):
        data_date = datetime.datetime(2008, 1, 1)
        series = wbdata.get_series(self.indicator, data_date=data_date)
        assert series.index.name == 'country'

    def testDateRange(self):
        data_date = (datetime.datetime(2008, 1, 1),
                     datetime.datetime(2010, 1, 1))
        series = wbdata.get_series(self.indicator, data_date=data_date,
                                   convert_date=True)
        assert min(series.index.get_level_values('date')).year == 2008
        assert max(series.index.get_level_values('date')).year == 2010

    def testConvertDate(self):
        series = wbdata.get_series(self.indicator, convert_date=True)
        assert isinstance(series.index.get_level_values('date')[0],
                          datetime.datetime)

    def testColumnName(self):
        series = wbdata.get_series(self.indicator, column_name='foo')
        assert series.name == 'foo'


class TestGetDataframe(unittest.TestCase):
    def setUp(self):
        self.indicators = {
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
        data_date = (datetime.datetime(2008, 1, 1),
                     datetime.datetime(2010, 1, 1))
        wbdata.get_dataframe(self.indicators, data_date=data_date)

    def testConvertDate(self):
        wbdata.get_dataframe(self.indicators, convert_date=True)

    def testColumnName(self):
        df = wbdata.get_dataframe(self.indicators)
        assert tuple(sorted(df.columns)) == ('gdp', 'gdppc')


if __name__ == '__main__':
    unittest.main()
