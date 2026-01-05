# RoboDash Development Makefile
# Usage: make <target>

.PHONY: help install install-dev lint format test test-cov screenshot clean run run-mock

# Default target
help:
	@echo "RoboDash Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Quality:"
	@echo "  lint         Run all linters (black, isort, flake8, mypy)"
	@echo "  format       Auto-format code with black and isort"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  screenshot   Run screenshot tests only"
	@echo ""
	@echo "Running:"
	@echo "  run          Run dashboard (requires CAN hardware)"
	@echo "  run-mock     Run dashboard with mock data"
	@echo ""
	@echo "Other:"
	@echo "  clean        Remove build artifacts and caches"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Code quality
lint:
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	isort src/ tests/

# Testing
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --tb=short --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

screenshot:
	pytest tests/ -v -m screenshot
	@echo "Screenshots saved to: tests/screenshots/"

# Running
run:
	python -m src.main

run-mock:
	python -m src.main --mock

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
