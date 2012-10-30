"""
wbdata.fetcher: retrieve and cache queries
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
import json
import logging
import os
import sys
import time

try:  # python 2
    import cPickle as pickle

    from urllib import urlencode
    from urllib2 import URLError
    from urllib2 import urlopen
except ImportError:  # python 3
    import pickle

    from urllib.request import urlopen
    from urlllib.error import URLError
    from urlllib.parse import urlencode

# Inspiration for below from Trent Mick and Sridhar Ratnakumar
# <http://pypi.python.org/pypi/appdirs/1.2.0>

if sys.platform.startswith("win"):
    BASEDIR = os.path.join(os.getenv("LOCALAPPDATA",
                                     os.getenv("APPDATA",
                                               os.path.expanduser("~"))),
                           "wbdata")
elif sys.platform is "darwin":
    BASEDIR = os.path.expanduser('~/Library/Caches')
else:
    BASEDIR = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))

CACHEDIR = os.path.join(BASEDIR, 'wbdata')
if not os.path.exists(CACHEDIR):
    os.mkdir(CACHEDIR)
CACHEPATH = os.path.join(CACHEDIR, "cache")
PER_PAGE = 1000
DATE_IDX = 0
DATA_IDX = 1
TRIES = 5


class Fetcher(object):
    """
    An object with a cache to retrieve and page responses from the World
    Bank API
    """
    def __init__(self):
        self.cache = None

    def __assert_cache(self):  # speeds up initial import
        """Create the cache if it isn't there"""
        if self.cache:
            return
        try:
            with open(CACHEPATH) as cachefile:
                self.cache = pickle.load(cachefile)
        except IOError:
            self.cache = {}

    def fetch(self, query_url, args=None, cached=True):
        """fetch data from the World Bank API or from cache

        :query_url: the base url to be queried
        :args: a dictionary of GET arguments
        :cached: use the cache
        :returns: a list of dictionaries containing the response to the query
        """
        if not args:
            args = []
        args.extend([("format", "json"), ("per_page", PER_PAGE)])
        query_url = "?".join((query_url, urlencode(args)))
        logging.debug("Query using {0}".format(query_url))
        results = self.__get_paged_data(query_url, cached)
        for i in results:
            if "id" in i:
                i['id'] = i['id'].strip()
        return results

    def prune(self, age=30):
        """Delete all entries more than age days old

        :age: the max age (in days) of an entry
        """
        self.__assert_cache()
        min_date = datetime.date.today().toordinal() - age
        for i in self.cache:
            if self.cache[i][DATE_IDX] < min_date:
                del(self.cache[i])
        self.sync_cache()

    def __get_paged_data(self, query_url, cached):
        """
        Page through results returned by query_url to return a single list
        """
        # TODO: This is a monster: break it up
        self.__assert_cache()
        results = []
        original_url = query_url
        while 1:
            if cached and query_url in self.cache:
                response = self.cache[query_url]
            else:
                response = self.__retrieve_url(query_url)
                self.cache[query_url] = response
                self.sync_cache()
            response = json.loads(response)
            if response is None:
                raise Exception(
                    "Got no response from query {0}".format(query_url))
            results.extend(response[1])
            this_page = response[0]['page']
            pages = response[0]['pages']
            logging.debug("Processed page {0} of {1}".format(this_page, pages))
            if this_page == pages:
                break
            query_url = original_url + "&page={0}".format(int(this_page + 1))
            time.sleep(1)
        return results

    def __retrieve_url(self, url):
        thistry = 0
        while 1:
            try:
                query = urlopen(url)
                response = query.read()
                query.close()
                break
            except URLError as e:
                if thistry < TRIES:
                    thistry += 1
                    continue
                else:
                    print(url)
                    raise e
        return response

    def sync_cache(self):
        """Sync cache to disk"""
        self.__assert_cache()
        with open(CACHEPATH, 'wb') as cachefile:
            pickle.dump(self.cache, cachefile,
                        protocol=pickle.HIGHEST_PROTOCOL)
