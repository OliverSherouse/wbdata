"""
wbdata: A wrapper for the World Bank API
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

from .api import (get_country, get_data, get_dataframe, get_panel,
                   get_indicator, get_incomelevel, get_lendingtype, get_source,
                   get_topic, search_countries, search_indicators)

__version__ = "0.2.1"
