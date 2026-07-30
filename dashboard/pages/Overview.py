import streamlit as st
import plotly.express as px

from database import get_connection
from queries import (
    overview_metrics,
    run_query,
    shipment_status,
    priority_distribution,
    shipment_timeline,
    risk_summary,
    warehouse_performance
)

from components.sidebar import render_sidebar
from components.filters import render_filters


st.title("📊 Shipping Analytics Overview")

render_sidebar()
render_filters()


# -------------------------
# GLOBAL FILTERS
# -------------------------

filters = {

    "warehouses":
        st.session_state.get(
            "warehouse_filter",
            []
        ),

    "statuses":
        st.session_state.get(
            "status_filter",
            []
        ),

    "priorities":
        st.session_state.get(
            "priority_filter",
            []
        ),

    "risk":
        st.session_state.get(
            "risk_filter",
            []
        )
}



# -------------------------
# KPI METRICS
# -------------------------

metrics = overview_metrics(filters).iloc[0]


a,b,c,d = st.columns(4)


a.metric(
    "Shipments",
    f"{int(metrics.shipments):,}"
)

b.metric(
    "Customers",
    f"{int(metrics.customers):,}"
)

c.metric(
    "Warehouses",
    f"{int(metrics.warehouses):,}"
)

d.metric(
    "Average Risk",
    f"{metrics.avg_risk:.1f}"
)



a,b,c,d = st.columns(4)


a.metric(
    "Avg Distance",
    f"{metrics.avg_distance:,.0f} km"
)

b.metric(
    "Avg Delivery",
    f"{metrics.avg_delivery:.1f} hrs"
)

c.metric(
    "Avg Package Weight",
    f"{metrics.avg_weight:.1f} kg"
)

d.metric(
    "Risk Score",
    f"{metrics.avg_risk:.0f}"
)


st.divider()



# -------------------------
# STATUS + PRIORITY
# -------------------------

left,right = st.columns(2)


status = shipment_status(filters)


fig = px.pie(
    status,
    names="status",
    values="shipments",
    title="Shipment Status"
)


left.plotly_chart(
    fig,
    use_container_width=True
)



priority = priority_distribution(filters)


fig = px.bar(
    priority,
    x="priority",
    y="shipments",
    color="priority",
    title="Priority Distribution"
)


right.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# SHIPMENT TREND
# -------------------------

st.subheader(
    "📈 Shipment Activity"
)


timeline = shipment_timeline(filters)


fig = px.line(
    timeline,
    x="date",
    y="shipments",
    markers=True
)


st.plotly_chart(
    fig,
    use_container_width=True
)



# -------------------------
# PACKAGE + WAREHOUSE
# -------------------------

left,right = st.columns(2)



sizes = run_query("""
SELECT

    package_size,

    COUNT(*) shipments

FROM delivery_performance

GROUP BY package_size

ORDER BY shipments DESC

""")


fig = px.bar(
    sizes,
    x="package_size",
    y="shipments",
    title="Package Size Distribution"
)


left.plotly_chart(
    fig,
    use_container_width=True
)



warehouse = warehouse_performance(filters)


fig = px.bar(
    warehouse,
    x="name",
    y="shipments",
    title="Warehouse Volume",
    color="shipments"
)


right.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# RISK SUMMARY
# -------------------------

st.subheader(
    "⚠️ Risk Overview"
)


risk = risk_summary(filters)


fig = px.bar(
    risk,
    x="risk_category",
    y="shipments",
    color="risk_category",
    title="Risk Distribution"
)


st.plotly_chart(
    fig,
    use_container_width=True
)