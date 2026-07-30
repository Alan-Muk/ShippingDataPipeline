import streamlit as st
import plotly.express as px

from database import get_connection

from components.sidebar import render_sidebar
from components.filters import render_filters


st.title("🏭 Warehouse Analytics")

render_sidebar()
render_filters()


con = get_connection()


# -------------------------
# KPI SECTION
# -------------------------

metrics = con.sql("""
SELECT
    COUNT(DISTINCT warehouse_id) AS warehouses,
    COUNT(order_id) AS shipments,
    AVG(distance_km) AS avg_distance,
    AVG(risk_score) AS avg_risk
FROM delivery_performance
""").df().iloc[0]


a, b, c, d = st.columns(4)


a.metric(
    "Warehouses",
    f"{int(metrics.warehouses)}"
)

b.metric(
    "Total Shipments",
    f"{int(metrics.shipments):,}"
)

c.metric(
    "Average Distance",
    f"{metrics.avg_distance:,.0f} km"
)

d.metric(
    "Average Risk",
    f"{metrics.avg_risk:.1f}"
)


st.divider()


# -------------------------
# WAREHOUSE PERFORMANCE
# -------------------------

st.subheader(
    "📦 Warehouse Performance"
)


warehouse = con.sql("""
SELECT
    w.name,
    w.city,
    w.country,
    w.capacity,

    COUNT(d.order_id) AS shipments,

    AVG(d.distance_km) AS avg_distance,

    AVG(d.estimated_delivery_hours)
        AS avg_delivery_hours,

    AVG(d.risk_score)
        AS avg_risk

FROM warehouses w

LEFT JOIN delivery_performance d
ON w.warehouse_id = d.warehouse_id

GROUP BY
    w.name,
    w.city,
    w.country,
    w.capacity

ORDER BY shipments DESC
""").df()


st.dataframe(
    warehouse,
    use_container_width=True
)


st.divider()


# -------------------------
# SHIPMENT VOLUME
# -------------------------

left, right = st.columns(2)


fig = px.bar(
    warehouse,
    x="name",
    y="shipments",
    color="shipments",
    title="Shipment Volume by Warehouse"
)


left.plotly_chart(
    fig,
    use_container_width=True
)


fig = px.bar(
    warehouse,
    x="name",
    y="avg_risk",
    color="avg_risk",
    title="Average Risk by Warehouse"
)


right.plotly_chart(
    fig,
    use_container_width=True
)


st.divider()


# -------------------------
# DELIVERY PERFORMANCE
# -------------------------

st.subheader(
    "🚚 Delivery Performance"
)


fig = px.scatter(
    warehouse,
    x="avg_distance",
    y="avg_delivery_hours",
    size="shipments",
    color="name",
    hover_name="name",
    title="Distance vs Delivery Time"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


st.divider()


# -------------------------
# CAPACITY VIEW
# -------------------------

st.subheader(
    "🏗 Warehouse Capacity Context"
)


capacity = warehouse.copy()


capacity["shipment_ratio"] = (
    capacity["shipments"]
    /
    capacity["capacity"]
)


fig = px.bar(
    capacity,
    x="name",
    y="shipment_ratio",
    color="shipment_ratio",
    title="Shipment Volume Compared With Capacity"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    "Capacity represents warehouse limits. "
    "Shipment ratio shows current simulated shipment volume "
    "relative to available capacity."
)


st.divider()


# -------------------------
# WAREHOUSE MAP
# -------------------------

st.subheader(
    "🌍 Warehouse Locations"
)


locations = con.sql("""
SELECT
    name,
    city,
    country,
    latitude,
    longitude
FROM warehouses
""").df()


fig = px.scatter_mapbox(
    locations,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=[
        "city",
        "country"
    ],
    zoom=3,
    height=500
)


fig.update_layout(
    mapbox_style="open-street-map"
)


st.plotly_chart(
    fig,
    use_container_width=True
)