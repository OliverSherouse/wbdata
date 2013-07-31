"""
wbdata.fetcher: retrieve and cache queries
"""

#Copyright (C) 2012-2013 Oliver Sherouse <Oliver DOT Sherouse AT gmail DOT com>

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

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import json
import logging
import os
import sys

try:  # python 2
    import cPickle as pickle

    from urllib import urlencode
    from urllib2 import URLError
    from urllib2 import urlopen
except ImportError:  # python 3
    import pickle

    from urllib.request import urlopen
    from urllib.error import URLError
    from urllib.parse import urlencode

PER_PAGE = 1000
TRIES = 5


class Cache(object):
    """Docstring for Cache """

    def __init__(self):
        """@todo: to be defined """
        self.__path = None
        self.__cache = None

    @property
    def path(self):
        if self.__path is None:
            # Inspiration for below from Trent Mick and Sridhar Ratnakumar
            # <http://pypi.python.org/pypi/appdirs/1.2.0>
            if sys.platform.startswith("win"):
                basedir = os.path.join(os.getenv("LOCALAPPDATA", os.getenv(
                    "APPDATA", os.path.expanduser("~"))), "wbdata")
            elif sys.platform is "darwin":
                basedir = os.path.expanduser('~/Library/Caches')
            else:
                basedir = os.getenv('XDG_CACHE_HOME',
                                    os.path.expanduser('~/.cache'))
            cachedir = os.path.join(basedir, 'wbdata')
            if not os.path.exists(cachedir):
                os.makedirs(cachedir)
            self.__path = os.path.join(cachedir, "cache")
        return self.__path

    @property
    def cache(self):
        if self.__cache is None:
            try:
                with open(self.path, 'rb') as cachefile:
                    try:
                        cache = pickle.load(cachefile, encoding="ascii",
                                            errors="replace")
                    except TypeError:
                        cache = pickle.load(cachefile)
            except IOError:
                cache = {}
            self.__cache = cache
        return self.__cache

    def __getitem__(self, key):
        return self.cache[key]

    def __setitem__(self, key, value):
        self.cache[key] = value
        self.sync()

    def __contains__(self, item):
        return item in self.cache

    def sync(self):
        """Sync cache to disk"""
        with open(self.path, 'wb') as cachefile:
            pickle.dump(self.cache, cachefile, protocol=2)

CACHE = Cache()


def fetch_url(url):
    """
    Fetch a url directly from the World Bank, up to TRIES tries

    :url: the  url to retrieve
    :returns: a string with the url contents
    """
    response = None
    for i in range(TRIES):
        try:
            query = urlopen(url)
            response = query.read()
            query.close()
            break
        except URLError:
            continue
    if response is None:
        raise ValueError
    try:
        return str(response, encoding="ascii", errors="replace")
    except TypeError:
        return str(response)


def fetch(query_url, args=None, cached=True):
    """fetch data from the World Bank API or from cache

    :query_url: the base url to be queried
    :args: a dictionary of GET arguments
    :cached: use the cache
    :returns: a list of dictionaries containing the response to the query
    """
    if args is None:
        args = []
    args.extend((("format", "json"), ("per_page", PER_PAGE)))
    query_url = "?".join((query_url, urlencode(args)))
    logging.debug("Query using {0}".format(query_url))
    results = []
    original_url = query_url
    pages, this_page = 0, 1
    while pages != this_page:
        if cached and query_url in CACHE:
            raw_response = CACHE[query_url]
        else:
            raw_response = fetch_url(query_url)
            CACHE[query_url] = raw_response
        response = json.loads(raw_response)
        if response is None:
            raise ValueError("Got no response")
        results.extend(response[1])
        this_page = response[0]['page']
        pages = response[0]['pages']
        logging.debug("Processed page {0} of {1}".format(this_page, pages))
        query_url = original_url + "&page={0}".format(int(this_page) + 1)

    for i in results:
        if "id" in i:
            i['id'] = i['id'].strip()
    return results
