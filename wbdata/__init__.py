"""
wbdata: A wrapper for the World Bank API
"""

from functools import lru_cache

from ._metadata import get_version
from .client import Client

__version__ = get_version()


@lru_cache(maxsize=1)
def get_default_client() -> Client:
    """
    Get the default client
    """
    return Client()


get_data = get_default_client().get_data
get_series = get_default_client().get_series
get_dataframe = get_default_client().get_dataframe
get_countries = get_default_client().get_countries
get_indicators = get_default_client().get_indicators
get_incomelevels = get_default_client().get_incomelevels
get_lendingtypes = get_default_client().get_lendingtypes
get_sources = get_default_client().get_sources
get_topics = get_default_client().get_topics
