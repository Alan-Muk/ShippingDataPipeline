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

DASHBOARD_DIR = PROJECT_ROOT / "dashboards"

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