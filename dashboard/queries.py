import streamlit as st

from database import get_connection


@st.cache_data
def run_query(sql):
    con = get_connection()

    return con.execute(sql).df()


def get_where(filters):
    from utils import build_where_clause

    if filters:
        return build_where_clause(filters)

    return ""


def overview_metrics(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        COUNT(*) AS shipments,

        COUNT(DISTINCT customer_id)
            AS customers,

        COUNT(DISTINCT warehouse_id)
            AS warehouses,

        AVG(distance_km)
            AS avg_distance,

        AVG(estimated_delivery_hours)
            AS avg_delivery,

        AVG(package_weight_kg)
            AS avg_weight,

        AVG(risk_score)
            AS avg_risk

    FROM delivery_performance

    {where}
    """
    )


def shipment_status(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        status,

        COUNT(*) shipments

    FROM delivery_performance

    {where}

    GROUP BY status

    ORDER BY shipments DESC
    """
    )


def priority_distribution(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        priority,

        COUNT(*) shipments

    FROM delivery_performance

    {where}

    GROUP BY priority

    ORDER BY shipments DESC
    """
    )


def shipment_timeline(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        DATE(order_date) date,

        COUNT(*) shipments

    FROM delivery_performance

    {where}

    GROUP BY date

    ORDER BY date
    """
    )


def risk_summary(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        risk_category,

        COUNT(*) shipments

    FROM delivery_performance

    {where}

    GROUP BY risk_category

    ORDER BY shipments DESC
    """
    )


def warehouse_performance(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        w.name,

        w.city,

        w.country,

        w.capacity,

        COUNT(d.order_id) shipments,

        AVG(d.distance_km)
            avg_distance,

        AVG(d.estimated_delivery_hours)
            avg_delivery_hours,

        AVG(d.risk_score)
            avg_risk

    FROM warehouses w

    LEFT JOIN delivery_performance d

    ON w.warehouse_id=d.warehouse_id

    {where}

    GROUP BY

        w.name,
        w.city,
        w.country,
        w.capacity

    ORDER BY shipments DESC
    """
    )


def route_performance(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        transport_mode,

        COUNT(*) shipments,

        AVG(distance_km)
            distance,

        AVG(estimated_hours)
            hours,

        AVG(distance_km / estimated_hours)
            speed

    FROM routes

    GROUP BY transport_mode

    ORDER BY speed DESC
    """
    )


def top_customers(filters=None):
    where = get_where(filters)

    return run_query(
        f"""
    SELECT

        c.first_name || ' ' || c.last_name
            AS customer,

        c.country,

        COUNT(f.order_id)
            shipments,

        AVG(f.package_weight_kg)
            avg_weight

    FROM dim_customers c

    JOIN fact_shipments f

    ON c.customer_id=f.customer_id

    JOIN delivery_performance d

    ON f.order_id=d.order_id

    {where}

    GROUP BY

        customer,

        c.country

    ORDER BY shipments DESC

    LIMIT 20
    """
    )
