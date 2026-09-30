from pathlib import Path

# ---------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

WAREHOUSE_DIR = PROJECT_ROOT / "warehouse"
DUCKDB_PATH = WAREHOUSE_DIR / "shipping.duckdb"

DBT_DIR = PROJECT_ROOT / "dbt" / "shipping_analytics"

DASHBOARD_DIR = PROJECT_ROOT / "dashboard"  # fixed: was "dashboards"

# ---------------------------------------------------------------------
# API Configuration
# ---------------------------------------------------------------------

RANDOM_USER_API = "https://randomuser.me/api/"

OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 10

# ---------------------------------------------------------------------
# Pipeline Defaults
# ---------------------------------------------------------------------

DEFAULT_CUSTOMER_COUNT = 100

DEFAULT_WAREHOUSE_COUNT = 4

DEFAULT_ORDERS_PER_CUSTOMER = 3

# Reproducibility — set to an int for deterministic synthetic data,
# or None for fresh data each run.
PIPELINE_SEED: int | None = None

# ---------------------------------------------------------------------
# Warehouse Table Registry
# ---------------------------------------------------------------------
# Maps DuckDB table name -> (layer, subdir, filename).
# The pipeline and WarehouseLoader both consume this so that table
# naming and source paths stay in sync.

WAREHOUSE_TABLES: dict[str, tuple[str, str, str]] = {
    "customers": ("silver", "customers", "customers.parquet"),
    "warehouses": ("silver", "warehouses", "warehouses.parquet"),
    "weather": ("silver", "weather", "weather.parquet"),
    "orders": ("silver", "orders", "orders.parquet"),
    "routes": ("gold", "routes", "routes.parquet"),
    "delivery_risk": ("gold", "delivery_risk", "delivery_risk.parquet"),
}

_LAYER_DIRS = {
    "bronze": BRONZE_DIR,
    "silver": SILVER_DIR,
    "gold": GOLD_DIR,
}


def table_source_path(table_name: str) -> Path:
    """Resolve a registered warehouse table to its parquet path."""
    if table_name not in WAREHOUSE_TABLES:
        raise KeyError(f"Unknown warehouse table: {table_name!r}")

    layer, subdir, filename = WAREHOUSE_TABLES[table_name]

    return _LAYER_DIRS[layer] / subdir / filename
