"""
Dashboard query utilities.

Builds WHERE clauses from the sidebar filter dict. Filter columns
are optionally qualified by a table alias so multi-table queries
work without ambiguity.
"""

from pathlib import Path

import duckdb
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "warehouse" / "shipping.duckdb"


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """Shared, read-only DuckDB connection to the warehouse."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse not found at {DB_PATH}. Run `python -m src.pipeline` first."
        )
    return duckdb.connect(str(DB_PATH), read_only=True)


# ---------------------------------------------------------------------
# WHERE-clause builder
# ---------------------------------------------------------------------


def _quote(value: str) -> str:
    """Single-quote a SQL string literal, escaping embedded quotes."""
    return "'" + value.replace("'", "''") + "'"


def build_where_clause(filters: dict | None, alias: str = "") -> str:
    """
    Build a WHERE clause from the filter dict.

    `alias` (if provided) prefixes every column reference, so the
    clause can be dropped into a JOIN without ambiguity:
        build_where_clause(filters, alias="d")
        -> "WHERE d.status IN ('shipped')"

    Returns "" if no filters are active.
    """
    if not filters:
        return ""

    prefix = f"{alias}." if alias else ""
    conditions: list[str] = []

    if filters.get("warehouses"):
        values = ",".join(_quote(w) for w in filters["warehouses"])
        conditions.append(
            f"{prefix}warehouse_id IN ("
            f"  SELECT warehouse_id FROM warehouses WHERE name IN ({values})"
            f")"
        )

    if filters.get("statuses"):
        values = ",".join(_quote(s) for s in filters["statuses"])
        conditions.append(f"{prefix}status IN ({values})")

    if filters.get("priorities"):
        values = ",".join(_quote(p) for p in filters["priorities"])
        conditions.append(f"{prefix}priority IN ({values})")

    if filters.get("risk"):
        values = ",".join(_quote(r) for r in filters["risk"])
        conditions.append(f"{prefix}risk_category IN ({values})")

    if not conditions:
        return ""

    return "WHERE " + " AND ".join(conditions)
