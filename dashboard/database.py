"""
DuckDB connection management for the dashboard.

Reads from the same warehouse the Python pipeline writes to.
Connection is opened read-only and cached for the app's lifetime.
"""

from pathlib import Path

import duckdb
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "warehouse" / "shipping.duckdb"


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a shared, read-only DuckDB connection to the warehouse."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse not found at {DB_PATH}. " f"Run `python -m src.pipeline` first."
        )
    return duckdb.connect(str(DB_PATH), read_only=True)
