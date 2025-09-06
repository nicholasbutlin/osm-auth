.PHONY: help setup

help:
	@echo "Common development commands:"
	@echo "  make setup     - Create a virtualenv in .venv and install dependencies from pyproject.toml"

setup:
	git init . && \
	rm -rf .venv && \
	uv sync --all-groups && \
	uv run pip install --upgrade pip && \
	uv run pre-commit autoupdate && \
	uv run pre-commit install


