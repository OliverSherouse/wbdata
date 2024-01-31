"""
wbdata: A wrapper for the World Bank API
"""

__version__ = "1.0.0"

from .client import Client


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
