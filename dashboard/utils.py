import duckdb
import streamlit as st
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "warehouse" / "shipping.duckdb"


@st.cache_resource
def get_connection():
    return duckdb.connect(str(DB_PATH), read_only=True)


@st.cache_data
def query(sql):
    con = get_connection()
    return con.execute(sql).df()


def build_where_clause(filters):
    conditions = []

    if filters["warehouses"]:
        values = ",".join([f"'{x}'" for x in filters["warehouses"]])

        conditions.append(
            f"""
            warehouse_id IN
            (
                SELECT warehouse_id
                FROM warehouses
                WHERE name IN ({values})
            )
            """
        )

    if filters["statuses"]:
        values = ",".join([f"'{x}'" for x in filters["statuses"]])

        conditions.append(f"status IN ({values})")

    if filters["priorities"]:
        values = ",".join([f"'{x}'" for x in filters["priorities"]])

        conditions.append(f"priority IN ({values})")

    if filters["risk"]:
        values = ",".join([f"'{x}'" for x in filters["risk"]])

        conditions.append(f"risk_category IN ({values})")

    if len(conditions) == 0:
        return ""

    return "WHERE " + " AND ".join(conditions)
