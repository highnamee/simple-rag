.PHONY: help setup setup-dev install install-dev format lint type-check security-check test clean all-checks pre-commit run ci

# Default target
help:
	@echo "Available commands:"
	@echo "  setup          - Production setup"
	@echo "  setup-dev      - Development setup"
	@echo "  install        - Install production dependencies only"
	@echo "  install-dev    - Install all dependencies (prod + dev)"
	@echo "  format         - Format code with black and isort"
	@echo "  lint          - Run flake8 linter"
	@echo "  type-check    - Run mypy type checker"
	@echo "  security-check - Run bandit security checker"
	@echo "  all-checks    - Run all quality checks"
	@echo "  pre-commit    - Install and run pre-commit hooks"
	@echo "  run           - Run the chat application"
	@echo "  clean         - Clean cache files"

# Production setup
setup:
	./bin/setup.sh

# Development setup
setup-dev:
	./bin/setup-dev.sh

# Installation targets
install:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt; \
	else \
		python3 -m pip install --upgrade pip && pip install -r requirements.txt; \
	fi

install-dev:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt; \
	else \
		python3 -m pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt; \
	fi

# Application runner
run:
	./bin/run.sh

# Code formatting
format:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && isort src/ chat.py && black src/ chat.py; \
	else \
		isort src/ chat.py && black src/ chat.py; \
	fi

# Linting
lint:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && flake8 src/ chat.py; \
	else \
		flake8 src/ chat.py; \
	fi

# Type checking
type-check:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && mypy src/ chat.py; \
	else \
		mypy src/ chat.py; \
	fi

# Security checking
security-check:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && (bandit -r src/ chat.py -f json || bandit -r src/ chat.py); \
	else \
		bandit -r src/ chat.py -f json || bandit -r src/ chat.py; \
	fi

# Run all checks
all-checks: lint type-check security-check
	@echo "All quality checks complete!"

# Pre-commit setup
pre-commit:
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && pre-commit install && pre-commit run --all-files; \
	else \
		pre-commit install && pre-commit run --all-files; \
	fi

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
