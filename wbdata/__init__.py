"""
wbdata: A wrapper for the World Bank API
"""

#Copyright (C) 2012  Oliver Sherouse <Oliver DOT Sherouse AT gmail DOT com>

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, unicode_literals

import datetime
import logging
import sys

try:
    import pandas as pd
except ImportError:
    pd = None

import fetcher

__all__ = ["fetcher"]
__version__ = "0.0.1"
INTERACTIVE = sys.__stdin__.isatty()
BASE_URL = "http://api.worldbank.org"
COUNTRIES_URL = "{0}/countries".format(BASE_URL)
ILEVEL_URL = "{0}/incomeLevels".format(BASE_URL)
INDICATOR_URL = "{0}/indicator".format(BASE_URL)
LTYPE_URL = "{0}/lendingTypes".format(BASE_URL)
SOURCES_URL = "{0}/sources".format(BASE_URL)
TOPIC_URL = "{0}/topics".format(BASE_URL)
INDIC_ERROR = "Cannot specify more than one of indicator, source, and topic"

FETCHER = fetcher.Fetcher()


def __assert_pandas():
    if not pd:
        raise ValueError("Pandas must be installed to be used")


def __parse_value_or_iterable(arg):
    if type(arg) in (int, str, unicode):
        return str(arg)
    return ";".join(arg)


def __parse_monthly_date(data_date):
    return data_date.strftime("%YM%m")


def __parse_quarterly_date(data_date):
    return "{0}Q{1}".format(data_date.year, data_date.month // 4 + 1)


def __parse_yearly_date(data_date):
    return data_date.strftime("%Y")


def __parse_data_date(frequency, data_date):
    if isinstance(data_date, datetime.date):
        try:
            return {"M": __parse_monthly_date,
                    "Q": __parse_quarterly_date,
                    "Y": __parse_yearly_date}[frequency](data_date)
        except KeyError:
            raise ValueError("Bad Frequency")
    elif len(data_date) == 2:
        try:
            parser = {"M": __parse_monthly_date,
                      "Q": __parse_quarterly_date,
                      "Y": __parse_yearly_date}[frequency]
            return ":".join((parser(data_date[0]), parser(data_date[1])))
        except KeyError:
            raise ValueError("Bad Frequency")
    raise TypeError("Bad data_date")


def __convert_year_to_datetime(yearstr):
    return datetime.datetime.strptime(yearstr, "%Y")


def __convert_month_to_datetime(monthstr):
    split = monthstr.split("M")
    return datetime.datetime(int(split[0]), int(split[1]), 1)


def __convert_quarter_to_datetime(quarterstr):
    split = quarterstr.split("Q")
    quarter = int(split[1])
    month = quarter * 3 - 2
    return datetime.datetime(int(split[0]), month, 1)


def __convert_dates_to_datetime(data, frequency):
    first = data[0]['date']
    if "M" in first:
        converter = __convert_month_to_datetime
    elif "Q" in first:
        converter = __convert_quarter_to_datetime
    else:
        converter = __convert_year_to_datetime

    for datum in data:
        datum['date'] = converter(datum['date'])
    return data


def __cast_float(value):
    """
    Return a floated value or none
    """
    try:
        return float(value)
    except ValueError:
        return None


def __convert_to_dataframe(data, column_name):
    """
    Convert a set of values to a dataframe with columns for country and date
    """
    __assert_pandas()
    return pd.DataFrame({"country": [i["country"]["value"] for i in data],
                         "date": [i["date"] for i in data],
                         column_name: [__cast_float(i["value"]) for i in data]
                         })


def get_data(indicator, countries="all", aggregates=None, data_date=None,
             mrv=None, gapfill=None, frequency=None, convert_date=True,
             pandas=False, column_name="value"):
    """
    Retrieve indicators for given countries and years

    :indicator: the desired indicator code
    :countries: a country code, sequence of country codes, or "all" (default)
    :aggregates: the regional or aggregate code, or sequence thereof
    :date: the desired date as a datetime object or a 2-sequence with
        start and end dates
    :mrv: the number of most recent values to retrieve
    :gapfill: with mrv, fills gaps with the most recent values
    :frequency: 'Q', 'M', or 'Y' for units with mrv
    :convert_date: if True, convert date field to a datetime.datetime object.
    :pandas: if True, return results as a pandas DataFrame
    :column_name: the desired name for the pandas column
    :returns: list of dictionaries or pandas DataFrame
    """
    query_url = COUNTRIES_URL
    if aggregates:
        if countries != "all":
            raise ValueError("Cannot Specify both countries and aggregates")
        try:
            c_part = __parse_value_or_iterable(aggregates)
        except TypeError:
            raise TypeError("aggregates must be a string, iterable, or None")
    else:
        try:
            c_part = __parse_value_or_iterable(countries)
        except TypeError:
            raise TypeError("'countries' must be a string or iterable'")
    query_url = "/".join((query_url, c_part, "indicators", indicator))
    args = []
    if data_date:
        args.append(("date", __parse_data_date(frequency, data_date)))
    if mrv:
        args.append(("MRV", mrv))
    if gapfill:
        args.append(("Gapfill", "Y"))
    if frequency:
        if frequency in ("M", "Q", "Y"):
            args.append(("frequency", frequency))
        else:
            raise ValueError("Bad Frequency")
    data = FETCHER.fetch(query_url, args)
    if convert_date:
        data = __convert_dates_to_datetime(data, frequency)
    if pandas:
        return __convert_to_dataframe(data, column_name)
    return data


def __id_only_query(query_url, id_or_ids, display):
    if display is None:
        display = INTERACTIVE
    if id_or_ids:
        query_url = "/".join((query_url, __parse_value_or_iterable(id_or_ids)))
    results = FETCHER.fetch(query_url)
    if display:
        print_ids_and_names(results)
    else:
        return results


def get_source(source_id=None, display=None):
    """
    Retrieve information on a source

    :source_id: an id number or sequence thereof.  None returns all sources
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: if display is False, a dictionary describing a source
    """
    return __id_only_query(SOURCES_URL, source_id, display)


def get_incomelevel(level_id=None, display=None):
    """
    Retrieve information on an income level aggregate

    :level_id: an id number or sequence thereof.  None returns all income level
        aggregates
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: if display is False a dictionary describing an income level
        aggregate
    """
    return __id_only_query(ILEVEL_URL, level_id, display)


def get_topic(topic_id=None, display=None):
    """
    Retrieve information on a topic

    :topic_id: an id number or sequence thereof.  None returns all topics
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: if display is False, a dictionary describing an income level
        aggregate
    """
    return __id_only_query(TOPIC_URL, topic_id, display)


def get_lendingtype(type_id=None, display=None):
    """
    Retrieve information on an income level aggregate

    :level_id: an id number or sequence thereof.  None returns all lending type
        aggregates
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: if display is False, a dictionary describing an lending type
        aggregate
    """
    return __id_only_query(LTYPE_URL, type_id, display)


def get_country(country_id=None, incomelevel=None, lendingtype=None,
                display=None):
    """
    Retrieve information on a country or regional aggregate.  Can specify
    either country_id, or the aggregates, but not both

    :country_id: an id or sequence thereof.  None returns all countries and
        aggregates.  incomelevel and lendingtype are mutually exclusive
    :incomelevel: desired incomelevel id or ids
    :lendingtype: desired lendingtype id or ids
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: if display is False, a dictionary describing an lending type
        aggregate
    """
    if display is None:
        display = INTERACTIVE
    if country_id:
        if incomelevel or lendingtype:
            raise ValueError("Can't specify country_id and aggregates")
        return __id_only_query(COUNTRIES_URL, country_id, display)
    args = []
    if incomelevel:
        args.append(("incomeLevel", __parse_value_or_iterable(incomelevel)))
    if lendingtype:
        args.append(("lendingType", __parse_value_or_iterable(lendingtype)))
    results = FETCHER.fetch(COUNTRIES_URL, args)
    if display:
        print_ids_and_names(results)
    else:
        return results


def get_indicator(indicator=None, source=None, topic=None, display=None):
    """
    Retrieve information about an indicator or indicators.  Only one of
    indicator, source, and topic can be specified.  Specifying none of the
    three will return all indicators.

    :indicator: the specific indicator code
    :source: a source id
    :topic: a topic id
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: if display is False, a list of dictionary objects representing
        indicators
    """
    if display is None:
        display = INTERACTIVE
    if indicator:
        if source or topic:
            raise ValueError(INDIC_ERROR)
        query_url = "/".join((INDICATOR_URL, indicator))
    elif source:
        if topic:
            raise ValueError(INDIC_ERROR)
        query_url = "/".join((SOURCES_URL, str(source), "indicators"))
    elif topic:
        query_url = "/".join((TOPIC_URL, str(topic), "indicators"))
    else:
        query_url = INDICATOR_URL
    results = FETCHER.fetch(query_url)
    if display:
        print_ids_and_names(results)
    else:
        return(results)


def search_indicators(query, source=None, topic=None, display=None):
    """
    Search indicators for a certain term.  Very simple.  Only one of source or
    topic can be specified. In interactive mode, will return None and print
    ids and names unless suppress_printing is True.

    :query: the term to match against indicator names
    :source: if present, id of desired source
    :topic: if present, id of desired topic
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: a list of dictionaries representing indicators if display is
        False
    """
    if display is None:
        display = INTERACTIVE
    indicators = get_indicator(source=source, topic=topic, display=False)
    lower = query.lower()
    matched = [i for i in indicators if lower in i["name"].lower()]
    if display:
        print_ids_and_names(matched)
    else:
        return matched


def search_countries(query, incomelevel=None, lendingtype=None, display=None):
    """
    Search countries by name.  Very simple search.

    :query: the string to match against country names
    :incomelevel: if present, search only the matching incomelevel
    :lendingtype: if present, search only the matching lendingtype
    :display: if True,print ids and names instead of returning results.
        Defaults to True if in interactive prompt, or False otherwise
    :returns: a list of dictionaries representing countries if display is
        False
    """
    if display is None:
        display = INTERACTIVE
    countries = get_country(incomelevel=incomelevel, lendingtype=lendingtype,
                            display=False)
    lower = query.lower()
    matched = [i for i in countries if lower in i["name"].lower()]
    if display:
        print_ids_and_names(matched)
    else:
        return matched


def print_ids_and_names(objs):
    """
    Courtesy function to display ids and names from lists returned by wbdata.
    This will mostly be useful in interactive mode.

    :objs: a list of dictionary objects as returned by wbdata
    """
    try:
        max_length = str(max((len(i['id']) for i in objs)))
    except ValueError:
        return
    for i in objs:
        try:
            templ = "{id:" + max_length + "}\t{name}"
            print(templ.format(**i))
        except KeyError:
            templ = "{id:" + max_length + "}\t{value}"
            print(templ.format(**i))


def get_dataframe_from_indicators(indicators, countries="all", aggregates=None,
                                  data_date=None, mrv=None, gapfill=None,
                                  frequency=None, convert_date=True):
    """
    Convenience function to download a set of indicators and merge them into
    a pandas dataframe on the 'country' and 'date' columns.

    :indicators: An dictionary where the keys are desired indicators and the
        values are the desired column names
    :countries: a country code, sequence of country codes, or "all" (default)
    :aggregates: the regional or aggregate code, or sequence thereof
    :data_date: the desired date as a datetime object or a 2-sequence with
        start and end dates
    :mrv: the number of most recent values to retrieve
    :gapfill: with mrv, fills gaps with the most recent values
    :frequency: 'Q', 'M', or 'Y' for units with mrv
    :convert_date: if True, convert date field to a datetime.datetime object.
    :returns: a pandas dataframe

    """
    __assert_pandas()
    merged = None
    for indicator in indicators:
        indic_df = get_data(indicator, countries, aggregates, data_date, mrv,
                            gapfill, frequency, convert_date, pandas=True,
                            column_name=indicators[indicator])
        if merged:
            merged = merged.merge(indic_df, on=["country", "date"])
        else:
            merged = indic_df
    return merged
