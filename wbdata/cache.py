"""
Caching functionality

"""
import datetime as dt
import logging
import os
from pathlib import Path
from typing import Union

import appdirs
import cachetools
import shelved_cache  # type: ignore[import-untyped]

from wbdata import __version__

log = logging.getLogger(__name__)

CACHE_PATH = os.getenv(
    "WBDATA_CACHE_PATH",
    os.path.join(
        appdirs.user_cache_dir(appname="wbdata", version=__version__), "cache"
    ),
)

try:
    TTL_DAYS = int(os.getenv("WBDATA_CACHE_TTL_DAYS", "7"))
except ValueError:
    logging.warning("Couldn't parse WBDATA_CACHE_TTL_DAYS value, defaulting to 7")
    TTL_DAYS = 7

try:
    MAX_SIZE = int(os.getenv("WBDATA_CACHE_MAX_SIZE", "100"))
except ValueError:
    logging.warning("Couldn't parse WBDATA_CACHE_MAX_SIZE value, defaulting to 100")
    MAX_SIZE = 100


def get_cache(
    path: Union[str, Path, None] = None,
    ttl_days: Union[int, None] = None,
    max_size: Union[int, None] = None,
) -> cachetools.Cache:
    """
    Create a persistent cache.


    Default caching functionality can be controlled with environment variables:

    * `WBDATA_CACHE_PATH`: path for the cache (default: system default
          application cache)
    * `WBDATA_CACHE_TTL_DAYS`: number of days to cache results (default: 7)
    * `WBDATA_CACHE_MAX_SIZE`: maximum number of items to cache (default: 100)


    The cache returned is a `shelved_cache.PersistentCache` that wraps a
    `cachetools.TTLCache` object with the desired parameters. The cache
    is cleaned up on load.

    Parameters:
        path: path to the cache. If `None`, value of `WBDATA_CACHE_PATH`
        ttl_days: number of days to cache results. If `None`, value of
            `WBDATA_CACHE_TTL_DAYS`
        max_size: maximum number of items to cache. If `None`, value of
            `WBDATA_CACHE_MAX_SIZE`.

    """
    path = path or CACHE_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    ttl_days = ttl_days or TTL_DAYS
    max_size = max_size or MAX_SIZE
    cache: cachetools.TTLCache = shelved_cache.PersistentCache(
        cachetools.TTLCache,
        filename=str(path),
        maxsize=max_size,
        ttl=dt.timedelta(days=ttl_days),
        timer=dt.datetime.now,
    )
    cache.expire()
    return cache
