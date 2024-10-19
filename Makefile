.PHONY: clean clean-build clean-pyc clean-test coverage dist help install lint lint/ruff

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint/ruff: ## check style with ruff
	ruff check


lint: lint/ruff ## check style

test: ## run tests quickly with the default Python
	pytest

coverage: ## check code coverage quickly with the default Python
	coverage run --source ispdb -m pytest
	coverage report -m --fail-under=94 > .coverage.txt
	git diff .coverage.txt

typecheck: ## checks types with mypy
	mypy

test-all: lint typecheck test coverage ## lint, typecheck, test and coverage

# release: dist ## package and upload a release
#	twine upload dist/*

# dist: clean ## builds source and wheel package
#	python3 setup.py sdist
#	python3 setup.py bdist_wheel
#	ls -l dist

# install: clean ## install the package to the active Python's site-packages
#	python3 setup.py install
