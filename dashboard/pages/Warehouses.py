"""Warehouse Analytics page."""

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from queries import get_where, run_query
from components.filters import render_filters
from components.sidebar import render_sidebar
from theme import RISK_CONTINUOUS_SCALE

st.title("🏭 Warehouse Analytics")

render_sidebar()
filters = render_filters()


metrics = run_query(f"""
    SELECT
        COUNT(DISTINCT warehouse_id) AS warehouses,
        COUNT(order_id)              AS shipments,
        AVG(distance_km)             AS avg_distance,
        AVG(risk_score)              AS avg_risk
    FROM delivery_performance
    {get_where(filters)}
    """).iloc[0]

if int(metrics.shipments) == 0:
    st.warning("No shipments match the current filters.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Active Warehouses", f"{int(metrics.warehouses)}")
b.metric("Total Shipments", f"{int(metrics.shipments):,}")
c.metric("Average Distance", f"{metrics.avg_distance:,.0f} km")
d.metric("Average Risk", f"{metrics.avg_risk:.1f}")

st.divider()

st.subheader("📦 Warehouse Performance")

warehouse = run_query(f"""
    SELECT
        w.name, w.city, w.country, w.capacity,
        COUNT(d.order_id)                 AS shipments,
        AVG(d.distance_km)                AS avg_distance,
        AVG(d.estimated_delivery_hours)   AS avg_delivery_hours,
        AVG(d.risk_score)                 AS avg_risk
    FROM warehouses w
    LEFT JOIN delivery_performance d ON w.warehouse_id = d.warehouse_id
    {get_where(filters, alias="d")}
    GROUP BY w.name, w.city, w.country, w.capacity
    ORDER BY shipments DESC
    """)

st.dataframe(warehouse, use_container_width=True, height=250)

st.divider()

left, right = st.columns(2)

fig = px.bar(
    warehouse,
    x="name",
    y="shipments",
    color="shipments",
    title="Shipment Volume by Warehouse",
)
fig.update_layout(xaxis_tickangle=-30)
left.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    warehouse,
    x="name",
    y="avg_risk",
    color="avg_risk",
    color_continuous_scale=RISK_CONTINUOUS_SCALE,
    title="Average Risk by Warehouse",
)
fig.update_layout(xaxis_tickangle=-30)
right.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🚚 Delivery Performance")

fig = px.scatter(
    warehouse,
    x="avg_distance",
    y="avg_delivery_hours",
    size="shipments",
    color="name",
    hover_name="name",
    title="Distance vs Delivery Time (bubble size = shipments)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🏗 Capacity Utilisation")

capacity = warehouse.copy()
max_shipments = capacity["shipments"].max()
capacity["utilisation_idx"] = (
    capacity["shipments"] / max_shipments * 100 if max_shipments else 0
)

fig = px.bar(
    capacity,
    x="name",
    y="utilisation_idx",
    color="utilisation_idx",
    color_continuous_scale="Blues",
    title="Relative Shipment Volume (busiest warehouse = 100)",
)
fig.update_layout(xaxis_tickangle=-30, yaxis_title="Relative index")
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Bars show each warehouse's shipment volume relative to the busiest "
    "warehouse in the current filtered view."
)

st.divider()

st.subheader("🌍 Warehouse Locations")

locations = run_query("""
    SELECT name, city, country, latitude, longitude
    FROM warehouses
    """)

fig = px.scatter_mapbox(
    locations,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=["city", "country"],
    zoom=3.5,
    center={"lat": 50, "lon": 6},
    height=500,
)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)
