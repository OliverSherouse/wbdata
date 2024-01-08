"""
wbdata.fetcher: retrieve and cache queries
"""

import contextlib
import dataclasses
import datetime as dt
import json
import logging
import pprint
from typing import Any, Dict, List, MutableMapping, NamedTuple, Tuple, Union

import backoff
import requests

PER_PAGE = 1000
TRIES = 3


def _strip_id(row: Dict[str, Any]) -> None:
    with contextlib.suppress(KeyError):
        row["id"] = row["id"].strip()  # type: ignore[union-attr]


Response = Tuple[Dict[str, Any], List[Dict[str, Any]]]


class ParsedResponse(NamedTuple):
    rows: List[Dict[str, Any]]
    page: int
    pages: int
    last_updated: Union[str, None]

    @classmethod
    def from_response(cls, response: Response) -> "ParsedResponse":
        try:
            return ParsedResponse(
                rows=response[1],
                page=int(response[0]["page"]),
                pages=int(response[0]["pages"]),
                last_updated=response[0].get("lastupdated"),
            )
        except (IndexError, KeyError) as e:
            try:
                message = response[0]["message"][0]
                raise RuntimeError(
                    f"Got error {message['id']} ({message['key']}): "
                    f"{message['value']}"
                ) from e
            except (IndexError, KeyError) as e:
                raise RuntimeError(
                    f"Got unexpected response:\n{pprint.pformat(response)}"
                ) from e


CacheKey = Tuple[str, Tuple[Tuple[str, Any], ...]]


class Result(List[Dict[str, Any]]):
    """
    List with a `last_updated` attribute. The `last_updated` attribute is either
    a datetime.datetime object or None.
    """

    def __init__(self, *args, last_updated: Union[dt.datetime, None] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_updated = last_updated


@dataclasses.dataclass
class Fetcher:
    """
    An object for making cached HTTP requests.

    Parameters:
        cache: a dictlike container for caching responses
        session: a requests session to use to make the requests, if `None`,
            create a new session
    """

    cache: MutableMapping[CacheKey, str]
    session: requests.Session = dataclasses.field(default_factory=requests.Session)

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=requests.exceptions.ConnectTimeout,
        max_tries=TRIES,
    )
    def _get_response_body(
        self,
        url: str,
        params: Dict[str, Any],
    ) -> str:
        """
        Fetch a url directly from the World Bank

        Parameters:
            url: the url to retrieve
            params: a dictionary of GET parameters

        Returns: a string with the response content
        """
        # Copy is for mocking. It's kind of depressing but not too expensive
        body = self.session.get(url=url, params={**params}).text
        return body

    def _get_response(
        self,
        url: str,
        params: Dict[str, Any],
        skip_cache=False,
    ) -> ParsedResponse:
        """
        Get single page response from World Bank API or from cache

        Parameters:
            query_url: the base url to be queried
            params: a dictionary of GET arguments
            skip_cache: bypass the cache

        Returns: parsed version of the API response
        """
        key = (url, tuple(sorted(params.items())))
        if not skip_cache and key in self.cache:
            body = self.cache[key]
        else:
            body = self._get_response_body(url, params)
            self.cache[key] = body
        return ParsedResponse.from_response(tuple(json.loads(body)))

    def fetch(
        self,
        url: str,
        params: Union[Dict[str, Any], None] = None,
        skip_cache: bool = False,
    ) -> Result:
        """Fetch data from the World Bank API or from cache.

        Given the base url, keep fetching results until there are no more pages.

        Parameters:
            url: the base url to be queried
            params: a dictionary of GET arguments
            skip_cache: bool: use the cache

        Returns:
            a list of dictionaries containing the response to the query
        """
        params = {**(params or {})}
        params["format"] = "json"
        params["per_page"] = PER_PAGE
        page, pages = -1, -2
        rows: List[Dict[str, Any]] = []
        while pages != page:
            response = self._get_response(
                url=url,
                params=params,
                skip_cache=skip_cache,
            )
            rows.extend(response.rows)
            page, pages = response.page, response.pages
            logging.debug(f"Processed page {page} of {pages}")
            params["page"] = page + 1
        for row in rows:
            _strip_id(row)
        last_updated = (
            None
            if not response.last_updated
            else dt.datetime.strptime(response.last_updated, "%Y-%m-%d")
        )
        return Result(rows, last_updated=last_updated)
