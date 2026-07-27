from importlib.metadata import version

import wbdata


def test_package_version_matches_distribution_metadata() -> None:
    assert wbdata.__version__ == version("wbdata")
