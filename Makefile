.PHONY: help

CURRENT_DIR = $(shell pwd)
LOCAL_ENV_FILE ?= $(CURRENT_DIR)/local.env
TEST_ENV_FILE ?= $(CURRENT_DIR)/tests/local.env
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

APP_HOST := $(or ${APP_HOST},${APP_HOST},0.0.0.0)
APP_PORT := $(or ${APP_PORT},${APP_PORT},8000)
PYTHONPATH := $(or ${PYTHONPATH},${PYTHONPATH},.)


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-17s\033[0m %s\n", $$1, $$2}'

# ============= General use-cases =============

check: linting test ## Linting python code and run tests in one command

# ============= General commands =============

install: ## Install all dependencies (need poetry!)
	@echo "\n${GREEN}Installing project dependencies${NC}"
	pip install --force-reinstall poetry
	poetry install

clean:  ## Clear temporary information, stop Docker containers
	@echo "\n${YELLOW}Clear cache directories${NC}"
	rm -rf .mypy_cache .pytest_cache .coverage
	poetry run pyclean .
	@rm -rf `find . -name __pycache__`
	@rm -rf `find . -type f -name '*.py[co]' `
	@rm -rf `find . -type f -name '*~' `
	@rm -rf `find . -type f -name '.*~' `
	@rm -rf `find . -type f -name '@*' `
	@rm -rf `find . -type f -name '#*#' `
	@rm -rf `find . -type f -name '*.orig' `
	@rm -rf `find . -type f -name '*.rej' `
	@rm -rf .coverage
	@rm -rf coverage.html
	@rm -rf coverage.xml
	@rm -rf htmlcov
	@rm -rf build
	@rm -rf cover
	@rm -rf .develop
	@rm -rf .flake
	@rm -rf .install-deps
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf dist
	@rm -rf test-reports

test-webserver:
	@echo "Starting test webserver..."
	poetry run \
	dotenv -f $(LOCAL_ENV_FILE) run \
	uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload --reload-dir=./app

webserver:
	@echo "Starting webserver..."
	poetry run \
	uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT}

test: ## Run unit-tests
	@echo "\n${GREEN}Running unit-tests${NC}"
	poetry run \
	dotenv -f $(TEST_ENV_FILE) run \
	pytest --disable-warnings --cov-report=term-missing --cov-report=html --cov-config=setup.cfg --cov=app . -x -s

fmt: ## Auto formatting python code
	@echo "\n${GREEN}Auto formatting python code with isort${NC}"
	poetry run isort . || true
	@echo "\n${GREEN}Auto formatting python code with black${NC}"
	poetry run black . || true

linting: flake8 isort black ## Linting python code


# ============= Other project specific commands =============

flake8: ## Linting python code with flake8
	@echo "\n${GREEN}Linting python code with flake8${NC}"
	poetry run flake8 app tests

isort: ## Linting python code with isort
	@echo "\n${GREEN}Linting python code with isort${NC}"
	poetry run isort app tests --check

black: ## Linting python code with black
	@echo "\n${GREEN}Linting python code with black${NC}"
	poetry run black --check app tests

mypy: ## Linting python code with mypy
	@echo "\n${GREEN}Linting python code with mypy${NC}"
	poetry run mypy app tests
