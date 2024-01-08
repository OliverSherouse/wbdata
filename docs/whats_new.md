# What's New

## What's new in wbdata 1.0

The 1.0 release of `wbdata` is not *quite* a full rewrite, but is pretty much the next best thing. The architecture has been reworked, function and argument names have been changed to be more consistent and clear, and a few dependencies have been added for better and more reliable functionality.


### Features

* Date arguments can now be strings, not just `datetime.datetime` objects. Strings can be in the year, month, or quarter formats used by the World Bank API or in any other format that can be handled by [dateparser][https://dateparser.readthedocs.io/en/latest/].
* Default cache behavior can be configured with environment variables, including the path, TTL, and max number of items to cache. See [Cache Module documentation](reference/cache.md) for details.
* Users can now create `Client` objects if they want to set cache behavior programmatically have multiple caches, or supply their own requests Session.
* Caching is now provided using the [shelved_cache](https://github.com/mariushelf/shelved_cache) and [cachetools](https://github.com/tkem/cachetools/) libraries. Since a lot of annoying bugs seemed to come from wbdata's home-rolled cache implementation, this should be a good quality-of-life improvement for many people.
* Type annotations are available.

### Breaking API Changes

* Supported version of Python are now 3.8+. 
* All of the metadata retrieval functions have been renamed to their plural forms to reflect the fact that they always return a sequence:

    | Old Name          | New Name           |
    |-------------------|--------------------|
    | `get_country`     | `get_countries`    |
    | `get_indicator`   | `get_indicators`   |
    | `get_incomelevel` | `get_incomelevels` |
    | `get_lendingtype` | `get_lendingtypes` |
    | `get_topic`       | `get_topics`       |
    | `get_source`      | `get_sources`      |

* The functions `search_countries` and `search_indicators` have been removed. Searching by name is now available using the `query` parameter of the `get_countries` and `get_indicators` functions.
* The parameter `data_date` has been renamed `date`.
* The parameter `convert_dates` has been renamed `parse_dates`.
* The parameter `cache` with a default value `True` has been replaced with a parameter `skip_cache` with a default value of `False`.

