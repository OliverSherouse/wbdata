import datetime as dt
import json
from unittest import mock

import pytest

from wbdata import fetcher


@pytest.fixture
def mock_fetcher() -> fetcher.Fetcher:
    return fetcher.Fetcher(cache={}, session=mock.Mock())


class MockHTTPResponse:
    def __init__(self, value):
        self.text = json.dumps(value)


def test_get_request_content(mock_fetcher):
    url = "http://foo.bar"
    params = {"baz": "bat"}
    expected = {"hello": "there"}
    mock_fetcher.session.get = mock.Mock(return_value=MockHTTPResponse(value=expected))
    result = mock_fetcher._get_response_body(url=url, params=params)
    mock_fetcher.session.get.assert_called_once_with(url=url, params=params)
    assert json.loads(result) == expected


@pytest.mark.parametrize(
    ["url", "params", "response", "expected"],
    (
        pytest.param(
            "http://foo.bar",
            {"baz": "bat"},
            [{"page": "1", "pages": "1"}, [{"hello": "there"}]],
            fetcher.ParsedResponse(
                rows=[{"hello": "there"}],
                page=1,
                pages=1,
                last_updated=None,
            ),
            id="No date",
        ),
        pytest.param(
            "http://foo.bar",
            {"baz": "bat"},
            [
                {"page": "1", "pages": "1", "lastupdated": "2023-02-01"},
                [{"hello": "there"}],
            ],
            fetcher.ParsedResponse(
                rows=[{"hello": "there"}],
                page=1,
                pages=1,
                last_updated="2023-02-01",
            ),
            id="with date",
        ),
    ),
)
def test_get_response(url, params, response, expected, mock_fetcher):
    mock_fetcher.session.get = mock.Mock(return_value=MockHTTPResponse(value=response))
    got = mock_fetcher._get_response(url=url, params=params)
    mock_fetcher.session.get.assert_called_once_with(url=url, params=params)
    assert got == expected
    assert mock_fetcher.cache[(url), (("baz", "bat"),)] == json.dumps(response)


def test_cache_used(mock_fetcher):
    url = "http://foo.bar"
    response = [
        {"page": "1", "pages": "1"},
        [{"hello": "there"}],
    ]
    params = {"baz": "bat"}
    expected = fetcher.ParsedResponse(
        rows=[{"hello": "there"}],
        page=1,
        pages=1,
        last_updated=None,
    )

    mock_fetcher.cache[(url), (("baz", "bat"),)] = json.dumps(response)
    mock_fetcher._get_response(url=url, params=params)
    got = mock_fetcher._get_response(url=url, params=params)
    assert got == expected
    assert mock_fetcher.cache[(url), (("baz", "bat"),)] == json.dumps(response)


def test_skip_cache(mock_fetcher):
    url = "http://foo.bar"
    response = [
        {"page": "1", "pages": "1"},
        [{"hello": "there"}],
    ]
    params = {"baz": "bat"}
    expected = fetcher.ParsedResponse(
        rows=[{"hello": "there"}],
        page=1,
        pages=1,
        last_updated=None,
    )
    mock_fetcher.session.get = mock.Mock(return_value=MockHTTPResponse(value=response))
    mock_fetcher.cache[(url), (("baz", "bat"),)] = json.dumps({"old": "garbage"})
    got = mock_fetcher._get_response(url=url, params=params, skip_cache=True)
    mock_fetcher.session.get.assert_called_once_with(url=url, params=params)
    assert got == expected
    assert mock_fetcher.cache[(url), (("baz", "bat"),)] == json.dumps(response)


@pytest.mark.parametrize(
    ["url", "params", "responses", "expected"],
    (
        pytest.param(
            "http://foo.bar",
            {"baz": "bat"},
            [
                [{"page": "1", "pages": "1"}, [{"hello": "there"}]],
            ],
            fetcher.Result([{"hello": "there"}], last_updated=None),
            id="No date",
        ),
        pytest.param(
            "http://foo.bar",
            {"baz": "bat"},
            [
                [
                    {"page": "1", "pages": "1", "lastupdated": "2023-02-01"},
                    [{"hello": "there"}],
                ],
            ],
            fetcher.Result([{"hello": "there"}], last_updated=dt.datetime(2023, 2, 1)),
            id="with date",
        ),
        pytest.param(
            "http://foo.bar",
            {"baz": "bat"},
            [
                [
                    {"page": "1", "pages": "2", "lastupdated": "2023-02-01"},
                    [{"hello": "there"}],
                ],
                [
                    {"page": "2", "pages": "2", "lastupdated": "2023-02-01"},
                    [{"howare": "you"}],
                ],
            ],
            fetcher.Result(
                [{"hello": "there"}, {"howare": "you"}],
                last_updated=dt.datetime(2023, 2, 1),
            ),
            id="paged with date",
        ),
        pytest.param(
            "http://foo.bar",
            {"baz": "bat"},
            [
                [
                    {"page": "1", "pages": "2", "lastupdated": "2023-02-01"},
                    [{"hello": "there"}],
                ],
                [
                    {"page": "2", "pages": "2"},
                    [{"howare": "you"}],
                ],
            ],
            fetcher.Result([{"hello": "there"}, {"howare": "you"}], last_updated=None),
            id="paged without date",
        ),
    ),
)
def test_fetch(url, params, responses, expected, mock_fetcher):
    mock_fetcher.session.get = mock.Mock(
        side_effect=[MockHTTPResponse(value=response) for response in responses]
    )

    got = mock_fetcher.fetch(url=url, params=params)
    expected_params = [
        {
            "per_page": fetcher.PER_PAGE,
            "format": "json",
            **({"page": i + 1} if i else {}),
            **params,
        }
        for i in range(len(responses))
    ]
    got_params = [i.kwargs["params"] for i in mock_fetcher.session.get.mock_calls]

    assert got == expected
    assert expected_params == got_params
    for response, rparams in zip(responses, expected_params):
        assert mock_fetcher.cache[url, tuple(sorted(rparams.items()))] == json.dumps(
            response
        )


@pytest.mark.parametrize(
    ["response", "expected"],
    [
        pytest.param(
            [{"message": [{"id": "baderror", "key": "nogood", "value": "dontlikeit"}]}],
            r"Got error baderror \(nogood\): dontlikeit",
            id="no rows",
        ),
        pytest.param(
            [
                {
                    "pages": 2,
                    "message": [
                        {"id": "baderror", "key": "nogood", "value": "dontlikeit"}
                    ],
                },
                [],
            ],
            r"Got error baderror \(nogood\): dontlikeit",
            id="no page",
        ),
        pytest.param(
            [
                {
                    "page": 1,
                    "message": [
                        {"id": "baderror", "key": "nogood", "value": "dontlikeit"}
                    ],
                },
                [],
            ],
            r"Got error baderror \(nogood\): dontlikeit",
            id="no pages",
        ),
        pytest.param(
            [
                {
                    "page": 1,
                    "message": [{"key": "nogood", "value": "dontlikeit"}],
                },
                [],
            ],
            r"Got unexpected response",
            id="improper error",
        ),
    ],
)
def test_parse_response_errors(response, expected):
    with pytest.raises(RuntimeError, match=expected):
        fetcher.ParsedResponse.from_response(response)
