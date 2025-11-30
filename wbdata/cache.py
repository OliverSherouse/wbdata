"""
Caching functionality

"""

import datetime as dt
import glob
import logging
import os
from pathlib import Path

import appdirs
import cachetools
import shelved_cache  # type: ignore[import-untyped]

from .version import __version__

log = logging.getLogger(__name__)


def _remove_cache_files(path: str | Path) -> None:
    """Remove all files associated with a shelve cache.

    Shelve databases can create files with various extensions depending on
    the underlying dbm implementation (.db, .dir, .bak, .dat, etc.).
    """
    path_str = str(path)
    # Remove files with extensions that shelve might create
    for pattern in [f"{path_str}", f"{path_str}.*"]:
        for filepath in glob.glob(pattern):
            try:
                os.remove(filepath)
                log.debug(f"Removed corrupted cache file: {filepath}")
            except OSError as e:
                log.warning(f"Failed to remove cache file {filepath}: {e}")

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
    path: str | Path | None = None,
    ttl_days: int | None = None,
    max_size: int | None = None,
) -> shelved_cache.PersistentCache:
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

    def _create_cache() -> shelved_cache.PersistentCache:
        return shelved_cache.PersistentCache(
            cachetools.TTLCache,
            filename=str(path),
            maxsize=max_size,
            ttl=dt.timedelta(days=ttl_days),
            timer=dt.datetime.now,
        )

    cache = _create_cache()
    try:
        cache.expire()
    except SystemError:
        # Cache file is corrupted, remove it and create a new one
        log.warning(
            f"Cache at {path} appears to be corrupted. Removing and recreating."
        )
        cache.close()
        _remove_cache_files(path)
        cache = _create_cache()
        cache.expire()
    return cache
