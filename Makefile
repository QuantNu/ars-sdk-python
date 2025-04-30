.PHONY: setup clean build test dist venv

# Default target
all: clean venv setup build test

# Create virtual environment
venv:
	python -m venv venv

# Setup development environment
setup: venv
	. venv/bin/activate && pip install -e ".[dev]"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete

# Build package
build:
	. venv/bin/activate && python setup.py build

# Run tests
test:
	. venv/bin/activate && pytest -xvs tests/

# Create distribution packages
dist: clean
	. venv/bin/activate && python setup.py sdist bdist_wheel

# Install package in development mode
dev:
	. venv/bin/activate && pip install -e .
