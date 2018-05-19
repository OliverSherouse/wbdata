"""
wbdata.fetcher: retrieve and cache queries
"""

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import logging
import json
import os
import sys
import datetime


try:  # python 2
    import cPickle as pickle
except ImportError:  # python 3
    import pickle

import requests

EXP = 7
PER_PAGE = 1000
TODAY = datetime.date.today()
TRIES = 5


class Cache(object):
    """Docstring for Cache """

    def __init__(self):
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
                    cache = {
                        i: (date, json)
                        for i, (date, json) in pickle.load(cachefile).items()
                        if (TODAY - datetime.date.fromordinal(date)).days < EXP
                    }
            except IOError:
                cache = {}
            self.__cache = cache
        return self.__cache

    def __getitem__(self, key):
        return self.cache[key][1]

    def __setitem__(self, key, value):
        self.cache[key] = TODAY.toordinal(), value
        self.sync()

    def __contains__(self, item):
        return item in self.cache

    def sync(self):
        """Sync cache to disk"""
        with open(self.path, 'wb') as cachefile:
            pickle.dump(self.cache, cachefile)


CACHE = Cache()


def get_json_from_url(url, args):
    """
    Fetch a url directly from the World Bank, up to TRIES tries

    : url: the  url to retrieve
    : args: a dictionary of GET arguments
    : returns: a string with the url contents
    """
    for i in range(TRIES):
        try:
            return requests.get(url, args).text
        except requests.ConnectionError:
            continue
    logging.error("Error connecting to {url}".format(url=url))
    raise RuntimeError("Couldn't connect to API")


def get_response(url, args, cached=True):
    """
    Get single page response from World Bank API or from cache
    : query_url: the base url to be queried
    : args: a dictionary of GET arguments
    : cached: use the cache
    : returns: a dictionary with the response from the API
    """
    logging.debug('fetching {}'.format(url))
    key = (url, tuple(sorted(args.items())))
    if (cached and key in CACHE):
        response = CACHE[key]
    else:
        response = get_json_from_url(url, args)
        if cached:
            CACHE[key] = response
    return json.loads(response)


def fetch(url, args=None, cached=True):
    """Fetch data from the World Bank API or from cache.

    Given the base url, keep fetching results until there are no more pages.

    : query_url: the base url to be queried
    : args: a dictionary of GET arguments
    : cached: use the cache
    : returns: a list of dictionaries containing the response to the query
    """
    if args is None:
        args = {}
    else:
        args = dict(args)
    args["format"] = "json"
    args["per_page"] = PER_PAGE
    results = []
    pages, this_page = 0, 1
    while pages != this_page:
        response = get_response(url, args, cached=cached)
        if response[1] is None:
            raise RuntimeError(
                'Received no Data from API. This indicator may be invalid or '
                'no longer available'
            )
        results.extend(response[1])
        this_page = response[0]['page']
        pages = response[0]['pages']
        logging.debug("Processed page {0} of {1}".format(this_page, pages))
        args['page'] = int(this_page) + 1
    for i in results:
        if "id" in i:
            i['id'] = i['id'].strip()
    return results
