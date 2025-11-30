setup:
	uv sync --all-extras --group dev
.PHONY: setup

format:
	uv run ruff format wbdata tests docs
.PHONY: format

lint:
	uv run ruff check wbdata tests
.PHONY: lint

typecheck:
	uv run ty check wbdata
.PHONY: typecheck

test:
	uv run pytest
.PHONY: test

check: format lint typecheck test
.PHONY: check
