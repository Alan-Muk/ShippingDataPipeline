"""Executive Overview page."""

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from queries import (
    get_where,
    overview_metrics,
    priority_distribution,
    risk_summary,
    run_query,
    shipment_status,
    shipment_timeline,
    warehouse_performance,
)
from components.filters import render_filters
from components.sidebar import render_sidebar
from theme import RISK_COLORS

st.title("📊 Executive Overview")

render_sidebar()
filters = render_filters()


metrics = overview_metrics(filters).iloc[0]

if int(metrics.shipments) == 0:
    st.warning("No shipments match the current filters.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Shipments", f"{int(metrics.shipments):,}")
b.metric("Customers", f"{int(metrics.customers):,}")
c.metric("Warehouses", f"{int(metrics.warehouses):,}")
d.metric("High-Risk", f"{int(metrics.high_risk_shipments):,}")

a, b, c, d = st.columns(4)
a.metric("Avg Distance", f"{metrics.avg_distance:,.0f} km")
b.metric("Avg Delivery", f"{metrics.avg_delivery:.1f} hrs")
c.metric("Avg Package Weight", f"{metrics.avg_weight:.1f} kg")
d.metric("Avg Risk Score", f"{metrics.avg_risk:.1f}")

st.divider()

left, right = st.columns(2)

status = shipment_status(filters)
fig = px.pie(status, names="status", values="shipments", title="Shipment Status")
left.plotly_chart(fig, use_container_width=True)

priority = priority_distribution(filters)
fig = px.bar(
    priority,
    x="priority",
    y="shipments",
    color="priority",
    title="Priority Distribution",
)
right.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("📈 Shipment Activity")

timeline = shipment_timeline(filters)
fig = px.line(timeline, x="date", y="shipments", markers=True)
fig.update_traces(line=dict(width=2))
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.divider()

left, right = st.columns(2)

where = get_where(filters)

sizes = run_query(f"""
    SELECT package_size, COUNT(*) AS shipments
    FROM delivery_performance
    {where}
    GROUP BY package_size
    ORDER BY shipments DESC
    """)
fig = px.bar(sizes, x="package_size", y="shipments", title="Package Size Distribution")
left.plotly_chart(fig, use_container_width=True)

warehouse = warehouse_performance(filters)
fig = px.bar(
    warehouse,
    x="name",
    y="shipments",
    title="Warehouse Volume",
    color="shipments",
)
fig.update_layout(xaxis_tickangle=-30)
right.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("⚠️ Risk Overview")

risk = risk_summary(filters)
fig = px.bar(
    risk,
    x="risk_category",
    y="shipments",
    color="risk_category",
    color_discrete_map=RISK_COLORS,
    title="Risk Distribution",
)
st.plotly_chart(fig, use_container_width=True)
