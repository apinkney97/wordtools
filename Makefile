.DEFAULT_GOAL := help

.PHONY: fmt
## Run autoformatter
fmt:
	uv run ruff check --fix
	uv run ruff format

.PHONY: typecheck
## Run type checker
typecheck:
	uv run mypy

.PHONY: coverage
## Run tests with coverage report
coverage:
	uv run pytest --cov=src --cov-report term-missing

.PHONY: test
## Run tests
test:
	uv run pytest

.PHONY: help
## Display this help message
help:
	@echo "$$(tput setaf 2)Available rules:$$(tput sgr0)";sed -ne"/^## /{h;s/.*//;:d" -e"H;n;s/^## /---/;td" -e"s/:.*//;G;s/\\n## /===/;s/\\n//g;p;}" ${MAKEFILE_LIST}|awk -F === -v n=$$(tput cols) -v i=4 -v a="$$(tput setaf 6)" -v z="$$(tput sgr0)" '{printf"- %s%s%s\n",a,$$1,z;m=split($$2,w,"---");l=n-i;for(j=1;j<=m;j++){l-=length(w[j])+1;if(l<= 0){l=n-i-length(w[j])-1;}printf"%*s%s\n",-i," ",w[j];}}'
