# Basic functionality

The basic functionality for `wbdata` users is provided by a set of functions in
the topic level package namespace.

## Data Retrieval

These are the functions for actually getting data values from the World Bank
API.

### Raw Data Retrieval

::: wbdata.client.Client.get_data
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4


### Pandas Data Retrieval

These functions require Pandas to be installed to work.

::: wbdata.client.Client.get_series
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4

::: wbdata.client.Client.get_dataframe
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4

## Metadata Retrieval

These functions, for the most part, are for finding the parameters you want to
put into the data retrieval functions. These all return
[SearchResult][wbdata.client.SearchResult], which are lists that pretty-print
the table in an interactive environment, and which contain dictionary
representations of the requested resource.

### Searchable Metadata

There are enough indicators and countries that it's annoying to look through 
them, so the functions for retrieving information about them can be narrowed
with additional facets and filtered with a search term or regular expression
supplied to the `query` parameter.

::: wbdata.client.Client.get_countries
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4


::: wbdata.client.Client.get_indicators
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4

### Indicator Facets

::: wbdata.client.Client.get_sources
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4

::: wbdata.client.Client.get_topics
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4

### Country Facets

::: wbdata.client.Client.get_incomelevels
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4

::: wbdata.client.Client.get_lendingtypes
    options:
        show_root_heading: true
        show_root_full_path: false
        heading_level: 4
