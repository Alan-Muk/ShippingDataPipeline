"""Delivery Risk Analytics page."""

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from queries import get_where, risk_summary, run_query
from components.filters import render_filters
from components.sidebar import render_sidebar
from theme import RISK_COLORS, RISK_CONTINUOUS_SCALE

st.title("⚠️ Delivery Risk Analytics")

render_sidebar()
filters = render_filters()

where = get_where(filters)


metrics = run_query(f"""
    SELECT
        COUNT(*)              AS shipments,
        AVG(risk_score)       AS avg_risk,
        MAX(risk_score)       AS max_risk,
        COUNT(*) FILTER (WHERE risk_category IN ('HIGH', 'CRITICAL'))
                              AS high_risk_count
    FROM delivery_performance
    {where}
    """).iloc[0]

if int(metrics.shipments) == 0:
    st.warning("No shipments match the current filters.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Shipments Analysed", f"{int(metrics.shipments):,}")
b.metric("Average Risk Score", f"{metrics.avg_risk:.1f}")
c.metric("Highest Risk Score", f"{int(metrics.max_risk)}")
d.metric("High-Risk Shipments", f"{int(metrics.high_risk_count):,}")

st.divider()

left, right = st.columns(2)

risk = risk_summary(filters)
fig = px.pie(
    risk,
    names="risk_category",
    values="shipments",
    color="risk_category",
    color_discrete_map=RISK_COLORS,
    title="Risk Category Distribution",
)
left.plotly_chart(fig, use_container_width=True)

scores = run_query(f"SELECT risk_score FROM delivery_performance {where}")
fig = px.histogram(scores, x="risk_score", nbins=20, title="Risk Score Distribution")
right.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🏭 Risk by Warehouse")

warehouse_risk = run_query(f"""
    SELECT
        w.warehouse_id, w.name,
        COUNT(d.order_id) AS shipments,
        AVG(d.risk_score) AS avg_risk
    FROM delivery_performance d
    JOIN warehouses w ON d.warehouse_id = w.warehouse_id
    {get_where(filters, alias="d")}
    GROUP BY w.warehouse_id, w.name
    ORDER BY avg_risk DESC
    """)

fig = px.bar(
    warehouse_risk,
    x="name",
    y="avg_risk",
    color="avg_risk",
    color_continuous_scale=RISK_CONTINUOUS_SCALE,
    title="Average Risk Score by Warehouse",
)
fig.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(warehouse_risk, use_container_width=True)

st.divider()

st.subheader("🌦 Weather Impact")

weather = run_query(
    f"SELECT temperature, wind_speed, risk_score FROM delivery_performance {where}"
)

fig = px.scatter(
    weather,
    x="temperature",
    y="risk_score",
    size="wind_speed",
    size_max=20,
    color="risk_score",
    color_continuous_scale=RISK_CONTINUOUS_SCALE,
    title="Temperature vs Risk Score (bubble size = wind speed)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🚨 Highest Risk Shipments")

high_risk = run_query(f"""
    SELECT
        route_id, order_id, warehouse_id, transport_mode,
        distance_km, estimated_delivery_hours,
        temperature, wind_speed, risk_score, risk_category
    FROM delivery_performance
    {where}
    ORDER BY risk_score DESC
    LIMIT 50
    """)

st.dataframe(high_risk, use_container_width=True, height=400)
