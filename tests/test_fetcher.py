import pytest

import wbdata.fetcher
import wbdata.api


def test_bad_indicator_error():
    expected = (
        r"Got error 120 \(Invalid value\): The provided parameter value is "
        r"not valid"
    )
    with pytest.raises(RuntimeError, match=expected):
        wbdata.fetcher.fetch(
            f"{wbdata.api.COUNTRIES_URL}/all/AINT.NOT.A.THING"
        )
