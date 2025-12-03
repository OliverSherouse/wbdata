"""
Caching functionality

"""

import datetime as dt
import logging
import os
import pickle
import shutil
from pathlib import Path

import appdirs
import cachetools
import shelved_cache  # type: ignore[import-untyped]

from .version import __version__

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
    path = Path(path or CACHE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    ttl_days = ttl_days or TTL_DAYS
    max_size = max_size or MAX_SIZE

    def _build_cache() -> shelved_cache.PersistentCache:
        return shelved_cache.PersistentCache(
            cachetools.TTLCache,
            filename=str(path),
            maxsize=max_size,
            ttl=dt.timedelta(days=ttl_days),
            timer=dt.datetime.now,
        )

    try:
        cache = _build_cache()
        cache.expire()
        return cache
    except (SystemError, EOFError, pickle.UnpicklingError, OSError) as exc:
        log.warning("Cache at %s failed to load (%s); recreating", path, exc)
        _clear_cache_files(path)

    cache = _build_cache()
    cache.expire()
    return cache


def _clear_cache_files(path: Path) -> None:
    """Remove shelve-backed cache files derived from *path*.

    Shelve implementations may create multiple files with suffixes (e.g. `.db`,
    `.bak`, `.dat`, `.dir`). Remove the base file and any siblings sharing its
    stem to ensure we start from a clean slate after corruption.
    """

    suffixes = (".db", ".bak", ".dat", ".dir")
    candidates = {path}
    candidates.update(path.parent.glob(f"{path.stem}.*"))
    candidates.update({path.with_suffix(suffix) for suffix in suffixes})
    for candidate in candidates:
        try:
            candidate.unlink()
        except FileNotFoundError:
            continue
        except (IsADirectoryError, PermissionError):
            shutil.rmtree(candidate, ignore_errors=True)
