"""
wbdata: A wrapper for the World Bank API

Copyright (C) 2012  Oliver Sherouse <oliver DOT sherouse AT gmail DOT com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function, unicode_literals

import datetime
import logging
import urllib
import urllib2
import json
import time


BASE_URL = "http://api.worldbank.org"
COUNTRIES_URL = "{0}/countries".format(BASE_URL)
ILEVEL_URL = "{0}/incomeLevels".format(BASE_URL)
INDICATOR_URL = "{0}/indicator".format(BASE_URL)
LTYPE_URL = "{0}/lendingTypes".format(BASE_URL)
SOURCES_URL = "{0}/sources".format(BASE_URL)
TOPIC_URL = "{0}/topic".format(BASE_URL)
PER_PAGE = 1000
INDIC_ERROR = "Cannot specify more than one of indicator, source, and topic"

def __parse_string_or_iterable(arg):
    """
    Return string if arg is a string or ';'-delimited string if arg is a
    sequence
    
    :returns: string
    """
    if isinstance(arg, basestring):
        return arg
    return ";".join(arg)

def __get_paged_data(query_url, args=None):
    """
    Page through queries and return a list of the results
    
    :query_url: the pageless query url
    :returns: the merged list of all results from all pages
    """
    if not args:
        args = []
    args.extend([("format", "json"), ("per_page", PER_PAGE)])
    query_url = "?".join((query_url, urllib.urlencode(args)))
    logging.debug("Query using {0}".format(query_url))
    print(query_url)
    results = []
    original_url = query_url
    while 1:
        query = urllib2.urlopen(query_url)
        response = json.load(query)
        query.close()
        results.extend(response[1])
        this_page = response[0]['page']
        pages = response[0]['pages']
        logging.debug("Processed page {0} of {1}".format(this_page, pages))
        if this_page == pages:
            break
        query_url = original_url + "&page={0}".format(int(this_page + 1))
        time.sleep(1)
    return results



def get_data_for_indicator(indicator, countries="all", aggregates=None,
                           data_date=None, mrv=None, gapfill=None,
                           frequency="Y"):
    """
    Retrieve indicators for given countries and years

    :indicator: the desired indicator code
    :countries: a country code, sequence of country codes, or "all" (default)
    :aggregates: the regional or aggregate code, or sequence thereof
    :date: the desired date as a datetime.date object or a 2-sequence with
    start and end dates, or None
    :returns: @todo
    """
    query_url = COUNTRIES_URL
    if aggregates:
        if countries != "all":
            raise ValueError("Cannot Specify both countries and aggregates")
        try:
            c_part = __parse_string_or_iterable(aggregates)
        except TypeError:
            raise TypeError("'aggregates' must be a string, iterable, or None")
    else:
        try:
            c_part = __parse_string_or_iterable(countries)
        except TypeError:
            raise TypeError("'countries' must be a string or iterable'")
    query_url = "/".join((query_url, c_part, "indicators", indicator))
    args = []
    if data_date:
        if isinstance(data_date, datetime.date):
            if frequency == "M":
                d_part = data_date.strftime("%YM%m")
            elif frequency == "Y":
                d_part = data_date.strftime("%Y")
            else:
                raise ValueError("Bad Frequency")
        elif len(data_date) == 2:
            if frequency == "M":
                d_part = ":".join((data_date[0].strftime("%YM%m"),
                                   data_date[1].strftime("%YM%m")))
            elif frequency == "Y":
                d_part = ":".join((data_date[0].strftime("%Y"),
                                   data_date[1].strftime("%Y")))
            elif frequency == "Q":
                d_part = "{0}Q{1}:{2}Q{3}".format(data_date[0].year,
                                                  data_date[0].month // 4,
                                                  data_date[1].month,
                                                  data_date[1].month // 4)
            else:
                raise ValueError("Bad Frequency")
        else:
            raise TypeError("Bad data_date")
        args.append(("date", d_part))
    if mrv:
        args.append(("MRV", mrv))
    if gapfill:
        args.append(("Gapfill", "Y"))
    return __get_paged_data(query_url)


def __id_only_query(query_url, id_or_ids):
    """@todo: Docstring for __id_only_query
    
    :query_url: @todo
    :id_or_ids: @todo
    :returns: @todo
    """
    if id_or_ids:
        if type(id_or_ids) == "int":
            query_url = "{0}/{1}".format(query_url, type)
        else:
            id_part = "/".join([str(i) for i in id_or_ids])
            query_url = "{0}/{1}".format(query_url, id_part)
    return __get_paged_data(query_url)


def get_source(source_id=None):
    """
    Retrieve information on a source
    
    :source_id: an id number or sequence thereof.  None returns all sources.
    :returns: @todo
    """
    return __id_only_query(SOURCES_URL, source_id)


def get_incomelevel(level_id=None):
    """@todo: Docstring for get_incomelevel
    
    :level_id: @todo
    :returns: @todo
    """
    return __id_only_query(ILEVEL_URL, level_id)


def get_lendingtype(type_id=None):
    """@todo: Docstring for get_lendingtype
    
    :level_id: @todo
    :returns: @todo
    """
    return __id_only_query(LTYPE_URL, type_id)


def get_indicator(indicator=None, source=None, topic=None):
    """@todo: Docstring for get_indicator
    
    :indicator: @todo
    :source: @todo
    :topic: @todo
    :returns: @todo
    """
    if indicator:
        if source or topic:
            raise ValueError(INDIC_ERROR)
        query_url = "/".join(INDICATOR_URL, indicator)
        return __get_paged_data(query_url)
    if source:
        if topic:
            raise ValueError(INDIC_ERROR)
        query_url = "/".join(SOURCES_URL, source, "indicators")
        return __get_paged_data(query_url)
    if topic:
        query_url = "/".join(TOPIC_URL, source, "indicators")
        return __get_paged_data(query_url)
    return __get_paged_data(INDICATOR_URL)
