# Repository Guidelines

## Quickstart
- Run `make setup` to install all extras and dev tools.
- Run `make check` to execute format (check), lint, ty check, and tests.
- Open pull requests against `master`.
- Do not commit or push unless explicitly instructed.

## Dev Loop
- Run `make format` (ruff format).
- Run `make lint` (ruff check wbdata tests).
- Run `make typecheck` (ty check wbdata).
- Run `make test` (pytest with coverage addopts from config).
- Preview docs with `uv run mkdocs serve`.

## Project Layout
- Keep code in `wbdata/` (client, caching, API helpers); treat `wbdata/version.py` as the single source of version.
- Add tests in `tests/` with `test_*.py` mirroring public APIs.
- Maintain docs in `docs/` and `mkdocs.yml`; adjust packaging/tooling in `pyproject.toml`.

## Style
- Use Python 4-space indent, snake_case; CapWords for classes; re-export via `__all__` when needed.
- Run ruff (PEP8, imports, Bugbear/Simplify) before commits.
- Preserve typing coverage (`py.typed`); prefer explicit types.

## Testing
- Add pytest cases under `tests/`; favor fixtures for network isolation.
- Maintain coverage by exercising new branches; include regression cases for reported bugs.

## PR Expectations
- Use conventional, imperative titles (e.g., `fix: improve caching`).
- Ensure format/lint/type/tests pass; document user-facing changes; include repro or screenshots when behavior shifts.
- Bump `wbdata/version.py` alongside changelog/release notes when shipping releases.
