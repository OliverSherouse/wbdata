"""Package metadata helpers."""

from __future__ import annotations

import json
import re
import subprocess
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from urllib.parse import unquote, urlparse

_PACKAGE_NAME = "wbdata"
_VERSION_TAG_RE = re.compile(
    r"^v?(?P<version>\d+(?:\.\d+)+)(?:-(?P<distance>\d+)-g[0-9a-f]+)?$"
)


def get_version() -> str:
    """Return the installed package version, with a source-tree fallback."""
    package_root = Path(__file__).resolve().parent
    try:
        dist = distribution(_PACKAGE_NAME)
    except PackageNotFoundError:
        return _scm_version(package_root.parent)

    dist_root = Path(str(dist.locate_file(""))).resolve()
    if package_root.is_relative_to(dist_root):
        return dist.version

    direct_url = dist.read_text("direct_url.json")
    if direct_url is not None:
        try:
            source_root = Path(unquote(urlparse(json.loads(direct_url)["url"]).path))
        except (KeyError, TypeError, ValueError):
            source_root = None
        if source_root is not None and package_root.is_relative_to(source_root):
            return dist.version

    # In direct source-tree imports, avoid reporting an unrelated installed
    # distribution's version. Editable installs have matching metadata and take
    # one of the branches above; raw checkouts fall back to git-derived text.
    return _scm_version(package_root.parent)


def _scm_version(repo_root: Path) -> str:
    try:
        describe = subprocess.check_output(
            [
                "git",
                "describe",
                "--tags",
                "--long",
                "--match",
                "v[0-9]*",
                "--dirty",
            ],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "0+unknown"

    dirty = describe.endswith("-dirty")
    if dirty:
        describe = describe.removesuffix("-dirty")

    match = _VERSION_TAG_RE.match(describe)
    if match is None:
        return "0+unknown"

    version = match.group("version")
    distance = match.group("distance")
    if distance in (None, "0"):
        if dirty:
            parts = version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            return f"{'.'.join(parts)}.dev0+dirty"
        return version

    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    dev_version = f"{'.'.join(parts)}.dev{distance}"
    if dirty:
        return f"{dev_version}+dirty"
    return dev_version
