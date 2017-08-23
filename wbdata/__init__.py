"""
wbdata: A wrapper for the World Bank API
"""

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

from .api import (get_country, get_data, get_dataframe, get_panel,
                  get_indicator, get_incomelevel, get_lendingtype, get_source,
                  get_topic, search_countries, search_indicators)

__version__ = "0.3.0-dev"
