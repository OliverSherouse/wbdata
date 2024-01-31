"""
The client class defines the wbdata client class and associated support classes.
"""

import contextlib
import dataclasses
import datetime as dt
import re
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Sequence, Tuple, Union

import decorator
import requests
import tabulate

try:
    import pandas as pd  # type: ignore[import-untyped]
except ImportError:
    pd = None


from . import cache, dates, fetcher

BASE_URL = "https://api.worldbank.org/v2"
COUNTRIES_URL = f"{BASE_URL}/countries"
ILEVEL_URL = f"{BASE_URL}/incomeLevels"
INDICATOR_URL = f"{BASE_URL}/indicators"
LTYPE_URL = f"{BASE_URL}/lendingTypes"
SOURCE_URL = f"{BASE_URL}/sources"
TOPIC_URL = f"{BASE_URL}/topics"


class SearchResult(List):
    """
    A list that prints out a user-friendly table when printed or returned on the
    command line


    Items are expected to be dict-like and have an "id" key and a "name" or
    "value" key
    """

    def __repr__(self) -> str:
        try:
            return tabulate.tabulate(
                [[o["id"], o["name"]] for o in self],
                headers=["id", "name"],
                tablefmt="simple",
            )
        except KeyError:
            return tabulate.tabulate(
                [[o["id"], o["value"]] for o in self],
                headers=["id", "value"],
                tablefmt="simple",
            )


if pd:

    class Series(pd.Series):
        """
        A `pandas.Series` with a `last_updated` attribute.


        The `last_updated` attribute is set when the `Series` is created but not
        automatically updated. Its value is either `None` or a `datetime.datetime`
        object.
        """

        def __init__(
            self,
            *args,
            last_updated: Union[None, dt.datetime] = None,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.last_updated = last_updated

        _metadata = ["last_updated"]

        @property
        def _constructor(self):
            return Series

    class DataFrame(pd.DataFrame):
        def __init__(
            self, *args, serieses: Union[Dict[str, Series], None] = None, **kwargs
        ):
            """
            A `pandas.DataFrame` with a `last_updated` attribute


            The `last_updated` attribute is set when the Series is created but not
            automatically updated. Its value is a dictionary where the keys are the
            column names and the values are `None` or a `datetime.datetime` object.
            """
            if serieses:
                super().__init__(serieses)
                self.last_updated: Union[Dict[str, Union[dt.datetime, None]], None] = {
                    name: s.last_updated for name, s in serieses.items()
                }
            else:
                super().__init__(*args, **kwargs)
                self.last_updated = None

        _metadata = ["last_updated"]

        @property
        def _constructor(self):
            return DataFrame
else:
    Series = Any  # type: ignore[misc, assignment]
    DataFrame = Any  # type: ignore[misc, assignment]


@decorator.decorator
def needs_pandas(f, *args, **kwargs):
    if pd is None:
        raise RuntimeError(f"{f.__name__} requires pandas")
    return f(*args, **kwargs)


def _parse_value_or_iterable(arg: Any) -> str:
    """
    If arg is a single value, return it as a string; if an iterable, return a
    ;-joined string of all values
    """
    if isinstance(arg, str):
        return arg
    if isinstance(arg, Iterable):
        return ";".join(str(i) for i in arg)
    return str(arg)


def _cast_float(value: str) -> Union[float, None]:
    """Return a value coerced to float or None"""
    with contextlib.suppress(ValueError, TypeError):
        return float(value)
    return None


def _filter_by_pattern(
    rows: Iterable[Dict[str, Any]], pattern=Union[str, re.Pattern]
) -> Generator[Dict[str, Any], None, None]:
    """Return a generator of rows matching the pattern"""
    if isinstance(pattern, str):
        pattern = re.compile(pattern, re.IGNORECASE)
    return (row for row in rows if pattern.search(row["name"]))


@dataclasses.dataclass
class Client:
    """
    The client object for the World Bank API.

    Most users will only need to create this if they need more than one cache,
    want to specify a cache programmatically rather than through environment
    variables, or want to specify a requests Session.

    Parameters:
        cache_path: path to the cache file
        cache_ttl_days: number of days to retain cached results
        cache_max_size: number of items to retain in the cache
        session: requests Session object to use to make requests
    """

    cache_path: Union[str, Path, None] = None
    cache_ttl_days: Union[int, None] = None
    cache_max_size: Union[int, None] = None
    session: Union[requests.Session, None] = None

    def __post_init__(self):
        self.fetcher = fetcher.Fetcher(
            cache=cache.get_cache(
                path=self.cache_path,
                ttl_days=self.cache_ttl_days,
                max_size=self.cache_max_size,
            )
        )
        self.has_pandas = pd is None

    def get_data(
        self,
        indicator: str,
        country: Union[str, Sequence[str]] = "all",
        date: Union[
            str,
            dt.datetime,
            Tuple[Union[str, dt.datetime], Union[str, dt.datetime]],
            None,
        ] = None,
        freq: str = "Y",
        source: Union[int, str, Sequence[Union[int, str]], None] = None,
        parse_dates: bool = False,
        skip_cache: bool = False,
    ) -> fetcher.Result:
        """
        Retrieve indicators for given countries and years

        Parameters:
            indicator: the desired indicator code
            country: a country code, sequence of country codes, or "all" (default)
            date: the desired date as a string, datetime object or a 2-tuple
                with start and end dates
            freq: the desired periodicity of the data, one of 'Y' (yearly), 'M'
                (monthly), or 'Q' (quarterly). The indicator may or may not
                support the specified frequency.
            source: the specific source to retrieve data from (defaults on API
                to 2, World Development Indicators)
            parse_dates: if True, convert date field to a datetime.datetime
                object.
            skip_cache: bypass the cache when downloading

        Returns:
            A list of dictionaries of observations
        """
        url = COUNTRIES_URL
        try:
            c_part = _parse_value_or_iterable(country)
        except TypeError as e:
            raise TypeError("'country' must be a string or iterable'") from e
        url = "/".join((url, c_part, "indicators", indicator))
        params: Dict[str, Any] = {}
        if date:
            params["date"] = dates.format_dates(date, freq)
        if source:
            params["source"] = source
        data = self.fetcher.fetch(url=url, params=params, skip_cache=skip_cache)
        if parse_dates:
            dates.parse_row_dates(data)
        return data

    def _id_only_query(self, url: str, id_: Any, skip_cache: bool) -> SearchResult:
        """
        Utility to retrieve information when ids are the only arguments

        Parameters:
            url: the base url to use for the query
            id_: an id or sequence of ids
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionary objects describing results
        """
        if id_:
            url = "/".join((url, _parse_value_or_iterable(id_)))
        return SearchResult(self.fetcher.fetch(url=url, skip_cache=skip_cache))

    def get_sources(
        self,
        source_id: Union[int, str, Sequence[Union[int, str]], None] = None,
        skip_cache: bool = False,
    ) -> SearchResult:
        """
        Retrieve information on one or more sources

        Parameters:
            source_id: a source id or sequence thereof.  None returns all sources
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionary objects describing selected sources
        """
        return self._id_only_query(url=SOURCE_URL, id_=source_id, skip_cache=skip_cache)

    def get_incomelevels(
        self,
        level_id: Union[int, str, Sequence[Union[int, str]], None] = None,
        skip_cache: bool = False,
    ) -> SearchResult:
        """
        Retrieve information on one or more income level aggregates

        Parameters:
            level_id: a level id or sequence thereof.  None returns all income level
                aggregates
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionary objects describing selected
                income level aggregates
        """
        return self._id_only_query(ILEVEL_URL, level_id, skip_cache=skip_cache)

    def get_topics(
        self,
        topic_id: Union[int, str, Sequence[Union[int, str]], None] = None,
        skip_cache: bool = False,
    ) -> SearchResult:
        """
        Retrieve information on one or more topics

        Parameters:
            topic_id: a topic id or sequence thereof.  None returns all topics
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionary objects describing selected topic
                aggregates
        """
        return self._id_only_query(TOPIC_URL, topic_id, skip_cache=skip_cache)

    def get_lendingtypes(
        self,
        type_id: Union[int, str, Sequence[Union[int, str]], None] = None,
        skip_cache: bool = False,
    ) -> SearchResult:
        """
        Retrieve information on one or more lending type aggregates

        Parameters:
            type_id: lending type id or sequence thereof.  None returns all lending
                type aggregates
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionary objects describing selected lending type aggregates
        """
        return self._id_only_query(LTYPE_URL, type_id, skip_cache=skip_cache)

    def get_countries(
        self,
        country_id: Union[str, Sequence[str], None] = None,
        query: Union[str, re.Pattern, None] = None,
        incomelevel: Union[int, str, Sequence[Union[int, str]], None] = None,
        lendingtype: Union[int, str, Sequence[Union[int, str]], None] = None,
        skip_cache: bool = False,
    ) -> SearchResult:
        """
        Retrieve information on one or more country or regional aggregates.

        You can filter your results by specifying `query, `incomelevel`, or
        `lendingtype`.  Specifying `query` will only return countries with
        names that match the query as a regular expression. If a string is
        supplied, the match is case insensitive.

        Specifying `query`, `incomelevel`, or `lendingtype` along with
        `country_id` will raise a `ValueError`.

        Parameters:
            country_id: a country id or sequence thereof. None returns all
                countries and aggregates.
            query: a regular expression on which to filter results
            incomelevel: desired incomelevel id or ids on which to filter results
            lendingtype: desired lendingtype id or ids on which to filter results
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionaries describing countries

        """
        if country_id:
            if incomelevel or lendingtype or query:
                raise ValueError("Can't specify country_id and aggregates")
            return self._id_only_query(COUNTRIES_URL, country_id, skip_cache=skip_cache)
        params = {}
        if incomelevel:
            params["incomeLevel"] = _parse_value_or_iterable(incomelevel)
        if lendingtype:
            params["lendingType"] = _parse_value_or_iterable(lendingtype)
        results = self.fetcher.fetch(
            url=COUNTRIES_URL, params=params, skip_cache=skip_cache
        )
        if query:
            results = _filter_by_pattern(results, query)
        return SearchResult(results)

    def get_indicators(
        self,
        indicator: Union[str, Sequence[str], None] = None,
        query: Union[str, re.Pattern, None] = None,
        source: Union[str, int, Sequence[Union[str, int]], None] = None,
        topic: Union[str, int, Sequence[Union[str, int]], None] = None,
        skip_cache: bool = False,
    ) -> SearchResult:
        """
        Retrieve information about an indicator or indicators.

        When called with no arguments, returns all indicators.  You can specify
        one or more indicators to retrieve, or you can specify a source or a
        topic for which to list all indicators.  Specifying more than one of
        `indicators`, `source`, and `topic` will raise a ValueError.

        Specifying `query` will only return indicators with names that match
        the query as a regular expression. If a string is supplied, the match
        is case insensitive. Specifying both `query` and `indicators` will raise
        a ValueError.

        Parameters:
            indicator: an indicator code or sequence thereof
            query: a regular expression on which to filter results
            source: a source id or sequence thereof
            topic: a topic id or sequence thereof
            skip_cache: bypass cache when downloading

        Returns:
            list of dictionary objects representing indicators
        """
        if query and indicator:
            raise ValueError("Cannot specify indicator and query")
        if sum(bool(i) for i in (indicator, source, topic)) > 1:
            raise ValueError(
                "Cannot specify more than one of indicator, source, and topic"
            )
        if indicator:
            url = "/".join((INDICATOR_URL, _parse_value_or_iterable(indicator)))
        elif source:
            url = "/".join((SOURCE_URL, _parse_value_or_iterable(source), "indicators"))
        elif topic:
            url = "/".join((TOPIC_URL, _parse_value_or_iterable(topic), "indicators"))
        else:
            url = INDICATOR_URL
        results = self.fetcher.fetch(url=url, skip_cache=skip_cache)
        if query:
            results = _filter_by_pattern(results, query)
        return SearchResult(results)

    @needs_pandas
    def get_series(
        self,
        indicator: str,
        country: Union[str, Sequence[str]] = "all",
        date: Union[
            str,
            dt.datetime,
            Tuple[Union[str, dt.datetime], Union[str, dt.datetime]],
            None,
        ] = None,
        freq: str = "Y",
        source: Union[int, str, Sequence[Union[int, str]], None] = None,
        parse_dates: bool = False,
        name: str = "value",
        keep_levels: bool = False,
        skip_cache: bool = False,
    ) -> Series:
        """
        Retrieve data for a single indicator as a pandas Series.

        If pandas is not installed, a RuntimeError will be raised.

        Parameters:
            indicator: the desired indicator code
            country: a country code, sequence of country codes, or "all" (default)
            date: the desired date as a string, datetime object or a 2-tuple
                with start and end dates
            freq: the desired periodicity of the data, one of 'Y' (yearly), 'M'
                (monthly), or 'Q' (quarterly). The indicator may or may not
                support the specified frequency.
            source: the specific source to retrieve data from (defaults on API
                to 2, World Development Indicators)
            parse_dates: if True, convert date field to a datetime.datetime
                object.
            skip_cache: bypass the cache when downloading
            name: the desired name for the pandas Series
            keep_levels: if True don't reduce the number of index
                levels returned if only getting one date or country
            skip_cache: bypass the cache when downloading

        Returns:
            Series with the requested data. The index of the series depends on
                the data returned and the specified options. If the data spans
                multiple dates and countries or if `keep_levels` is `True`, the
                index will be a 2-level MultiIndex with levels "country" and
                "name". If `keep_levels` is `False` (the default) and the data
                only has one country or date, the level with only one value
                will be dropped. If `keep_levels` is `False` and both levels
                only have one value, the country level is dropped.
        """
        raw_data = self.get_data(
            indicator=indicator,
            country=country,
            date=date,
            freq=freq,
            source=source,
            parse_dates=parse_dates,
            skip_cache=skip_cache,
        )
        df = pd.DataFrame(
            [[i["country"]["value"], i["date"], i["value"]] for i in raw_data],
            columns=["country", "date", name],
        )
        df[name] = df[name].map(_cast_float)
        if not keep_levels and len(df["country"].unique()) == 1:
            df = df.set_index("date")
        elif not keep_levels and len(df["date"].unique()) == 1:
            df = df.set_index("country")
        else:
            df = df.set_index(["country", "date"])
        return Series(df[name], last_updated=raw_data.last_updated)

    @needs_pandas
    def get_dataframe(
        self,
        indicators: Dict[str, str],
        country: Union[str, Sequence[str]] = "all",
        date: Union[
            str,
            dt.datetime,
            Tuple[Union[str, dt.datetime], Union[str, dt.datetime]],
            None,
        ] = None,
        freq: str = "Y",
        source: Union[int, str, Sequence[Union[int, str]], None] = None,
        parse_dates: bool = False,
        keep_levels: bool = False,
        skip_cache: bool = False,
    ) -> DataFrame:
        """
        Download a set of indicators and  merge them into a pandas DataFrame.

        If pandas is not installed, a RuntimeError will be raised.

        Parameters:
            indicators: An dictionary where the keys are desired indicators and the
                values are the desired column names country: a country code,
                sequence of country codes, or "all" (default)
            date: the desired date as a string, datetime object or a 2-tuple
                with start and end dates
            freq: the desired periodicity of the data, one of 'Y' (yearly), 'M'
                (monthly), or 'Q' (quarterly). The indicator may or may not
                support the specified frequency.
            source: the specific source to retrieve data from (defaults on API
                to 2, World Development Indicators)
            parse_dates: if True, convert date field to a datetime.datetime
                object.
            skip_cache: bypass the cache when downloading
            keep_levels: if True don't reduce the number of index
                levels returned if only getting one date or country
            skip_cache: bypass the cache when downloading

        Returns:
            DataFrame with one column per indicator. The index of the DataFrame
                depends on the data returned and the specified options. If the
                data spans multiple dates and countries or if `keep_levels` is
                `True`, the index will be a 2-level MultiIndex with levels
                "country" and "name". If `keep_levels` is `False` (the default)
                and the data only has one country or date, the level with only
                one value will be dropped. If `keep_levels` is `False` and both
                levels only have one value, the country level is dropped.

        """
        df = DataFrame(
            serieses={
                name: self.get_series(
                    indicator=indicator,
                    country=country,
                    date=date,
                    freq=freq,
                    source=source,
                    parse_dates=parse_dates,
                    keep_levels=True,
                    skip_cache=skip_cache,
                )
                for indicator, name in indicators.items()
            }
        )
        if not keep_levels and len(set(df.index.get_level_values(0))) == 1:
            df.index = df.index.droplevel(0)
        elif not keep_levels and len(set(df.index.get_level_values(1))) == 1:
            df.index = df.index.droplevel(1)
        return df
