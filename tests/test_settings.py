from pathlib import Path

from src.config.settings import (
    PROJECT_ROOT,
    DATA_DIR,
    BRONZE_DIR,
    SILVER_DIR,
    GOLD_DIR,
    WAREHOUSE_DIR,
    DUCKDB_PATH,
    DBT_DIR,
    DASHBOARD_DIR,
    RANDOM_USER_API,
    OPEN_METEO_API,
    REQUEST_TIMEOUT,
    DEFAULT_CUSTOMER_COUNT,
    DEFAULT_WAREHOUSE_COUNT,
    DEFAULT_ORDERS_PER_CUSTOMER,
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()


def test_data_directory():
    assert DATA_DIR == PROJECT_ROOT / "data"


def test_bronze_directory():
    assert BRONZE_DIR == DATA_DIR / "bronze"


def test_silver_directory():
    assert SILVER_DIR == DATA_DIR / "silver"


def test_gold_directory():
    assert GOLD_DIR == DATA_DIR / "gold"


def test_warehouse_directory():
    assert WAREHOUSE_DIR == PROJECT_ROOT / "warehouse"


def test_duckdb_path():
    assert DUCKDB_PATH == (WAREHOUSE_DIR / "shipping.duckdb")

    assert DUCKDB_PATH.suffix == ".duckdb"


def test_dbt_directory():
    assert DBT_DIR == (PROJECT_ROOT / "dbt" / "shipping_analytics")


def test_dashboard_directory():
    assert DASHBOARD_DIR == (PROJECT_ROOT / "dashboards")


def test_api_urls():
    assert RANDOM_USER_API.startswith("https://")

    assert OPEN_METEO_API.startswith("https://")


def test_request_timeout():
    assert REQUEST_TIMEOUT > 0


def test_pipeline_defaults():
    assert DEFAULT_CUSTOMER_COUNT > 0

    assert DEFAULT_WAREHOUSE_COUNT > 0

    assert DEFAULT_ORDERS_PER_CUSTOMER > 0
