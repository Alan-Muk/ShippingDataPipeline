
---

## 3. `Makefile` (NEW)

Create `Makefile` at the project root:

```makefile
# ShippingDataPipeline — local development commands
#
# Usage:
#   make help          Show this help
#   make install       Install package + dev deps
#   make lint          Check style with ruff
#   make fmt           Auto-format with ruff
#   make test          Run pytest
#   make test-cov      Run pytest with coverage
#   make integration   Run only integration tests
#   make pipeline      Run the Python ETL pipeline
#   make dbt           Run dbt models and tests
#   make ci            Run the full CI surface locally
#   make clean         Remove caches and build artifacts

.PHONY: help install lint fmt test test-cov integration pipeline dbt ci clean

PYTHON  ?= python
PYTEST  ?= pytest
RUFF    ?= ruff
DBT     ?= dbt

help:
	@echo "ShippingDataPipeline — available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package + dev dependencies
	$(PYTHON) -m pip install -e ".[dev]"

lint:  ## Check style with ruff
	$(RUFF) check .
	$(RUFF) format --check .

fmt:  ## Auto-format with ruff
	$(RUFF) format .

test:  ## Run pytest (excludes integration tests)
	$(PYTEST) tests/ -v

test-cov:  ## Run pytest with coverage
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing

integration:  ## Run only the integration tests
	$(PYTEST) tests/ -v -m integration

pipeline:  ## Run the full Python ETL pipeline
	$(PYTHON) -m src.pipeline

dbt:  ## Run dbt models and tests
	cd dbt/shipping_analytics && $(DBT) run && $(DBT) test

ci: lint test dbt  ## Run the full CI surface locally

clean:  ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .coverage coverage.xml htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd dbt/shipping_analytics && $(DBT) clean || true