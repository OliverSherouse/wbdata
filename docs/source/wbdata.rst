wbdata library reference
========================

Wbdata provides a set of functions that are used to interface with the World
Bank's databases.  For any function involving pandas capabilities, pandas must
(obviously) be installed.

Convenience Functions
---------------------
.. autofunction:: wbdata.search_indicators
.. autofunction:: wbdata.search_countries
.. autofunction:: wbdata.print_ids_and_names
.. autofunction:: wbdata.get_dataframe

Finding the data you want
-------------------------
.. autofunction:: wbdata.get_source
.. autofunction:: wbdata.get_topic
.. autofunction:: wbdata.get_lendingtype
.. autofunction:: wbdata.get_incomelevel
.. autofunction:: wbdata.get_country
.. autofunction:: wbdata.get_indicator

Retrieving your data
--------------------
.. autofunction:: wbdata.get_data
