#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals

import datetime
import json
import logging
import unittest

import wbdata

from tests import strings

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


class TestSimpleQueries(unittest.TestCase):
    def testGetAllIncomeLevels(self):
        wbdata.get_incomelevel()

    def testOneIncomeLevel(self):
        wbdata.get_incomelevel("OEC")

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
        expected = json.loads(strings.USA_DATA)
        got = wbdata.get_country(country_id="USA")
        self.assertEqual(expected, got)

    def testOEC(self):
        expected = json.loads(strings.OEC_DATA)
        got = wbdata.get_country(incomelevel="OEC")
        self.assertEqual(expected, got)

    def testIDB(self):
        expected = json.loads(strings.IDB_DATA)
        got = wbdata.get_country(lendingtype="IDB")
        self.assertEqual(expected, got)

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
        wbdata.get_indicator("SH.XPD.PRIV.ZS")

    def testGetIndicatorBySource(self):
        wbdata.get_indicator(source=1)

    def testGetIndicatorByTopic(self):
        wbdata.get_indicator(topic="1")

    @unittest.expectedFailure
    def testGetIndicatorBySourceAndTopic(self):
        wbdata.get_indicator(source="1", topic=1)


class TestGetData(unittest.TestCase):
    def testIndicator(self):
        wbdata.get_data("SH.XPD.PRIV.ZS")

    def testOneCountry(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country="USA")

    def testTwoCountries(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country=("chn", "bra"))

    def testDate(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country="usa",
                        data_date=datetime.datetime(2006, 1, 1))

    def testDateRange(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country="usa",
                        data_date=(datetime.datetime(2006, 1, 1),
                                   datetime.datetime(2010, 1, 1)))

    def testConvertDate(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country="usa", convert_date=True)

    def testPandas(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country="usa", pandas=True)

    def testColumnName(self):
        wbdata.get_data("SH.XPD.PRIV.ZS", country="usa", pandas=True,
                        column_name="IForget")


class TestSearchFunctions(unittest.TestCase):
    def testSearchCountry(self):
        wbdata.search_countries("United")

    def testSearchIndicators(self):
        wbdata.search_indicators("gdp")


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

if __name__ == '__main__':
    unittest.main()
