.PHONY: install test lint format check demo

install:
	python -m pip install -e ".[dev]"

test:
	pytest --cov=phd_search_agent --cov-branch --cov-report=term-missing

lint:
	ruff check .

format:
	ruff check . --fix

check: lint test

demo:
	phd-agent init --force
	phd-agent import-example examples/opportunities/safe-autonomy.yaml
	phd-agent dashboard
