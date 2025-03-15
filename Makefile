
.PHONY: fmt
fmt:
	uv run ruff check --fix
	uv run ruff format

.PHONY: typecheck
typecheck:
	uv run mypy

.PHONY: coverage
coverage:
	uv run pytest --cov=src --cov-report term-missing

.PHONY: test
test:
	uv run pytest
