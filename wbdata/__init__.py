"""
wbdata: A wrapper for the World Bank API
"""
__version__ = "0.3.0"

from .api import (  # noqa: F401
    get_country,
    get_data,
    get_series,
    get_dataframe,
    get_indicator,
    get_incomelevel,
    get_lendingtype,
    get_source,
    get_topic,
    search_countries,
    search_indicators,
)
