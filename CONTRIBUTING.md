# Contributing

## Pull request titles

Pull request titles must use Conventional Commits syntax, because squash merges use
the PR title as the commit message that drives automated releases.

Examples:

- `feat: add a new data helper` -> minor release
- `fix: correct cache expiry` -> patch release
- `feat!: remove a deprecated API` -> major release
- `fix: handle missing values` with a `BREAKING CHANGE:` footer -> major release

Prefer squash merges so the merged commit on `main`/`master` keeps the validated
PR title.

## Releases and versions

Versions come from git tags, not committed version files. Merged Conventional
Commits are analyzed on pushes to `main`/`master`; when a release is needed,
semantic-release creates a `vX.Y.Z` tag and GitHub release without committing a
version bump back to the branch.

Package builds use `setuptools-scm`, so a build from `vX.Y.Z` produces version
`X.Y.Z`. Local development builds between tags receive setuptools-scm dev
versions.

Publishing to PyPI happens only from release tags. The tag workflow builds with
uv and publishes with `uv publish`.

## Local checks

```bash
uv sync --all-extras --group dev
uv run pytest
uv tool run ty check
uv run python -m build
uvx twine check dist/*
```
