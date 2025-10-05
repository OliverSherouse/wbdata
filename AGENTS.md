# Repository Guidelines

## Project Structure & Module Organization
Source lives in `wbdata/` with clients, caching helpers, and API utilities; `wbdata/version.py` centralizes the library version and should be the single source when updating releases. Tests reside in `tests/` with `test_*.py` modules mirroring public APIs. Contributor-facing docs and MkDocs content sit in `docs/`, while packaging metadata and tooling configuration are in `pyproject.toml`.

## Build, Test, and Development Commands
Install dependencies with `poetry install` (add `--with tests,types,dev` for full tooling). Use `poetry run pytest` for the default suite and coverage, matching the `--cov=wbdata` addopts in configuration. Run `poetry run ruff check wbdata tests` to lint, and `poetry run mypy wbdata` for type validation. During documentation work, serve the site locally via `poetry run mkdocs serve`.

## Coding Style & Naming Conventions
Follow standard Python formatting with four-space indentation and readable, snake_case symbols. Public APIs exposed in `wbdata/__init__.py` should maintain descriptive, lowercase names; classes stay in CapWords. Ruff enforces PEP 8, import sorting, and selected Bugbear/Simplify rules—run it before committing. Keep modules typed, updating `py.typed` coverage when adding packages, and prefer explicit re-exports in `__all__` blocks where applicable.

## Testing Guidelines
Write new tests under `tests/` using `pytest` conventions (`test_feature.py`, functions starting with `test_`). When adding network-heavy scenarios, leverage fixtures to isolate HTTP calls. Keep coverage from `pytest-cov` stable by exercising new branches, and include regression cases that mirror reported issues.

## Commit & Pull Request Guidelines
Aim for concise, imperative subjects, optionally prefixed with Conventional Commit types as seen in `git log` (e.g., `fix: improve caching`). Reference related issues or discussions with `(#123)` in the subject when merging via GitHub. Before opening a PR, ensure lint, typing, and tests pass, document user-facing changes, and provide a short summary plus reproduction or screenshots when behavior shifts.

## Documentation & Release Notes
Update `docs/` pages when modifying user workflows, and verify the navigation using the MkDocs preview. Release metadata lives in `wbdata/version.py`; bump it in sync with changelog entries and confirm that packaging files (`pyproject.toml`, `MANIFEST.in`) need no extra updates.
