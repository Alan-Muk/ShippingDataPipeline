"""
Dashboard queries.

All queries return pandas DataFrames and accept an optional
`filters` dict (warehouse / status / priority / risk selections).
"""

import streamlit as st

from database import get_connection
from utils import build_where_clause

# ---------------------------------------------------------------------
# Low-level execution
# ---------------------------------------------------------------------


@st.cache_data(ttl=60)
def run_query(sql: str):
    """Run SQL against the warehouse and return a pandas DataFrame."""
    con = get_connection()
    return con.sql(sql).df()


def get_where(filters: dict | None, alias: str = "") -> str:
    """Build a WHERE clause from the filter dict (or '' if empty)."""
    if not filters:
        return ""
    return build_where_clause(filters, alias=alias)


# ---------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------


def overview_metrics(filters: dict | None = None):
    where = get_where(filters)
    return run_query(f"""
        SELECT
            COUNT(*)                        AS shipments,
            COUNT(DISTINCT customer_id)     AS customers,
            COUNT(DISTINCT warehouse_id)    AS warehouses,
            AVG(distance_km)                AS avg_distance,
            AVG(estimated_delivery_hours)   AS avg_delivery,
            AVG(package_weight_kg)          AS avg_weight,
            AVG(risk_score)                 AS avg_risk,
            COUNT(*) FILTER (
                WHERE risk_category IN ('HIGH', 'CRITICAL')
            )                               AS high_risk_shipments
        FROM delivery_performance
        {where}
        """)


def shipment_status(filters: dict | None = None):
    where = get_where(filters)
    return run_query(f"""
        SELECT status, COUNT(*) AS shipments
        FROM delivery_performance
        {where}
        GROUP BY status
        ORDER BY shipments DESC
        """)


def priority_distribution(filters: dict | None = None):
    where = get_where(filters)
    return run_query(f"""
        SELECT priority, COUNT(*) AS shipments
        FROM delivery_performance
        {where}
        GROUP BY priority
        ORDER BY shipments DESC
        """)


def shipment_timeline(filters: dict | None = None):
    where = get_where(filters)
    return run_query(f"""
        SELECT DATE(order_date) AS date, COUNT(*) AS shipments
        FROM delivery_performance
        {where}
        GROUP BY date
        ORDER BY date
        """)


def risk_summary(filters: dict | None = None):
    where = get_where(filters)
    return run_query(f"""
        SELECT risk_category, COUNT(*) AS shipments
        FROM delivery_performance
        {where}
        GROUP BY risk_category
        ORDER BY CASE risk_category
            WHEN 'LOW'      THEN 1
            WHEN 'MEDIUM'   THEN 2
            WHEN 'HIGH'     THEN 3
            WHEN 'CRITICAL' THEN 4
        END
        """)


# ---------------------------------------------------------------------
# Warehouse / routes
# ---------------------------------------------------------------------


def warehouse_performance(filters: dict | None = None):
    where = get_where(filters, alias="d")
    return run_query(f"""
        SELECT
            w.name,
            w.city,
            w.country,
            w.capacity,
            COUNT(d.order_id)                 AS shipments,
            AVG(d.distance_km)                AS avg_distance,
            AVG(d.estimated_delivery_hours)   AS avg_delivery_hours,
            AVG(d.risk_score)                 AS avg_risk
        FROM warehouses w
        LEFT JOIN delivery_performance d ON w.warehouse_id = d.warehouse_id
        {where}
        GROUP BY w.name, w.city, w.country, w.capacity
        ORDER BY shipments DESC
        """)


def route_performance(filters: dict | None = None):
    """Route stats grouped by transport mode (reads from delivery_performance
    so the filter WHERE clause — which references status/priority/risk — applies)."""
    where = get_where(filters)
    return run_query(f"""
        SELECT
            transport_mode,
            COUNT(*)                                     AS shipments,
            AVG(distance_km)                             AS distance,
            AVG(estimated_delivery_hours)                AS hours,
            SUM(distance_km) / NULLIF(SUM(estimated_delivery_hours), 0) AS speed
        FROM delivery_performance
        {where}
        GROUP BY transport_mode
        ORDER BY speed DESC
        """)


def top_customers(filters: dict | None = None):
    where = get_where(filters, alias="d")
    return run_query(f"""
        SELECT
            d.customer_id,
            c.first_name || ' ' || c.last_name AS customer,
            c.country,
            COUNT(d.order_id)                  AS shipments,
            AVG(d.package_weight_kg)           AS avg_weight
        FROM delivery_performance d
        JOIN dim_customers    c ON d.customer_id = c.customer_id
        {where}
        GROUP BY d.customer_id, customer, c.country
        ORDER BY shipments DESC
        LIMIT 20
        """)
