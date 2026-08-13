import streamlit as st
import plotly.express as px

from queries import run_query, risk_summary

from components.sidebar import render_sidebar
from components.filters import render_filters

st.title("⚠️ Delivery Risk Analytics")

render_sidebar()
render_filters()


# -------------------------
# GLOBAL FILTERS
# -------------------------

filters = {
    "warehouses": st.session_state.get("warehouse_filter", []),
    "statuses": st.session_state.get("status_filter", []),
    "priorities": st.session_state.get("priority_filter", []),
    "risk": st.session_state.get("risk_filter", []),
}


# -------------------------
# KPI SECTION
# -------------------------

metrics = run_query(
    """
SELECT

    COUNT(*) AS shipments,

    AVG(risk_score) AS avg_risk,

    MAX(risk_score) AS max_risk,

    AVG(temperature) AS avg_temperature

FROM delivery_performance

"""
).iloc[0]


a, b, c, d = st.columns(4)


a.metric("Shipments Analysed", f"{int(metrics.shipments):,}")

b.metric("Average Risk Score", f"{metrics.avg_risk:.1f}")

c.metric("Highest Risk Score", f"{int(metrics.max_risk)}")

d.metric("Average Temperature", f"{metrics.avg_temperature:.1f} °C")


st.divider()


# -------------------------
# RISK DISTRIBUTION
# -------------------------

left, right = st.columns(2)


risk = risk_summary(filters)


fig = px.pie(
    risk,
    names="risk_category",
    values="shipments",
    title="Risk Category Distribution",
    color="risk_category",
)


left.plotly_chart(fig, use_container_width=True)


scores = run_query(
    """
SELECT

    risk_score

FROM delivery_performance

"""
)


fig = px.histogram(scores, x="risk_score", nbins=20, title="Risk Score Distribution")


right.plotly_chart(fig, use_container_width=True)


st.divider()


# -------------------------
# RISK BY WAREHOUSE
# -------------------------

st.subheader("🏭 Risk by Warehouse")


warehouse_risk = run_query(
    """
SELECT

    w.name,

    COUNT(d.order_id) shipments,

    AVG(d.risk_score) avg_risk

FROM delivery_performance d

JOIN warehouses w

ON d.warehouse_id = w.warehouse_id

GROUP BY w.name

ORDER BY avg_risk DESC

"""
)


fig = px.bar(
    warehouse_risk,
    x="name",
    y="avg_risk",
    color="avg_risk",
    title="Average Risk Score by Warehouse",
)


st.plotly_chart(fig, use_container_width=True)


st.dataframe(warehouse_risk, use_container_width=True)


st.divider()


# -------------------------
# WEATHER IMPACT
# -------------------------

st.subheader("🌦 Weather Impact")


weather = run_query(
    """
SELECT

    temperature,

    wind_speed,

    risk_score

FROM delivery_performance

"""
)


fig = px.scatter(
    weather,
    x="temperature",
    y="risk_score",
    size="wind_speed",
    color="risk_score",
    title="Temperature vs Risk Score",
)


st.plotly_chart(fig, use_container_width=True)


st.divider()


# -------------------------
# HIGH RISK SHIPMENTS
# -------------------------

st.subheader("🚨 Highest Risk Shipments")


high_risk = run_query(
    """
SELECT

    order_id,

    warehouse_id,

    distance_km,

    estimated_delivery_hours,

    temperature,

    wind_speed,

    risk_score,

    risk_category

FROM delivery_performance

ORDER BY risk_score DESC

LIMIT 50

"""
)


st.dataframe(high_risk, use_container_width=True)
