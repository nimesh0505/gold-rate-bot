.PHONY: help test test-verbose coverage clean install lint

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  test-verbose- Run tests with verbose output"
	@echo "  coverage    - Run tests with coverage report"
	@echo "  clean       - Clean up cache files"
	@echo "  lint        - Run linting"

install:
	pip install -r requirements.txt

test:
	pytest

test-verbose:
	pytest -v

coverage:
	pytest --cov=app --cov-report=html --cov-report=term-missing

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

lint:
	python -m pytest --collect-only -q
