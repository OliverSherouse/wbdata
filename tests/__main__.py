#!/usr/bin/env python

import json
import logging
import unittest

import pandas
import wbdata

from tests import strings

logging.basicConfig(level=logging.DEBUG)


class TestSimpleQueries(unittest.TestCase):
    def testGetAllIncomeLevels(self):
        wbdata.get_incomelevel()

    def testOneIncomeLevel(self):
        wbdata.get_incomelevel("OEC")

    def testGetAllLendingTypes(self):
        wbdata.get_lendingtype()

    def testOneIncomeLevel(self):
        wbdata.get_lendingtype("IBD")

    def testGetAllSources(self):
        wbdata.get_source()

    def testOneSource(self):
        wbdata.get_source(31)

    def testGetAllTopics(self):
        wbdata.get_source()

    def testOneTopic(self):
        wbdata.get_source("3")


class GetCountryTestCase(unittest.TestCase):
    def testAllCountries(self):
        data = wbdata.get_country()

    def testUSA(self):
        expected = json.loads(strings.USA_DATA)
        got = wbdata.get_country(country_id="USA")
        self.assertEqual(expected, got)

    def testOEC(self):
        expected = json.loads(strings.OEC_DATA)
        got = wbdata.get_country(incomelevel="OEC")
        self.assertEqual(expected, got)

    def testOEC_NOC(self):
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
if __name__ == '__main__':
    unittest.main()
