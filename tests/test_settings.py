"""
Tests for src/config/settings.py.
"""

from src.config.settings import (
    BRONZE_DIR,
    DATA_DIR,
    DASHBOARD_DIR,
    DBT_DIR,
    DEFAULT_CUSTOMER_COUNT,
    DEFAULT_ORDERS_PER_CUSTOMER,
    DEFAULT_WAREHOUSE_COUNT,
    DUCKDB_PATH,
    GOLD_DIR,
    OPEN_METEO_API,
    PROJECT_ROOT,
    REQUEST_TIMEOUT,
    SILVER_DIR,
    WAREHOUSE_DIR,
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()


def test_data_directory():
    assert DATA_DIR == PROJECT_ROOT / "data"


def test_medallion_directories():
    assert BRONZE_DIR == DATA_DIR / "bronze"
    assert SILVER_DIR == DATA_DIR / "silver"
    assert GOLD_DIR == DATA_DIR / "gold"


def test_warehouse_directory():
    assert WAREHOUSE_DIR == PROJECT_ROOT / "warehouse"


def test_duckdb_path():
    assert DUCKDB_PATH == WAREHOUSE_DIR / "shipping.duckdb"
    assert DUCKDB_PATH.suffix == ".duckdb"


def test_dbt_directory():
    assert DBT_DIR == PROJECT_ROOT / "dbt" / "shipping_analytics"


def test_dashboard_directory():
    # NOTE: singular "dashboard" — the "dashboards" plural was a typo.
    assert DASHBOARD_DIR == PROJECT_ROOT / "dashboard"


def test_open_meteo_api_is_https():
    assert OPEN_METEO_API.startswith("https://")


def test_request_timeout_is_positive():
    assert REQUEST_TIMEOUT > 0


def test_pipeline_defaults_are_positive():
    assert DEFAULT_CUSTOMER_COUNT > 0
    assert DEFAULT_WAREHOUSE_COUNT > 0
    assert DEFAULT_ORDERS_PER_CUSTOMER > 0
