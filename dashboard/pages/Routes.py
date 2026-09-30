"""Route Analytics page."""

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from queries import get_where, run_query
from components.filters import render_filters
from components.sidebar import render_sidebar

st.title("🚛 Route Analytics")

render_sidebar()
filters = render_filters()

where = get_where(filters)


metrics = run_query(f"""
    SELECT
        COUNT(*)                                                    AS routes,
        AVG(distance_km)                                            AS avg_distance,
        AVG(estimated_delivery_hours)                               AS avg_hours,
        SUM(distance_km) / NULLIF(SUM(estimated_delivery_hours), 0) AS avg_speed
    FROM delivery_performance
    {where}
    """).iloc[0]

if int(metrics.routes) == 0:
    st.warning("No routes match the current filters.")
    st.stop()

a, b, c, d = st.columns(4)
a.metric("Total Routes", f"{int(metrics.routes):,}")
b.metric("Average Distance", f"{metrics.avg_distance:,.0f} km")
c.metric("Average Delivery Time", f"{metrics.avg_hours:.1f} hrs")
d.metric("Effective Fleet Speed", f"{metrics.avg_speed:.1f} km/hr")

st.divider()

st.subheader("🚚 Transport Performance")

transport = run_query(f"""
    SELECT
        transport_mode,
        COUNT(*)                                                    AS shipments,
        AVG(distance_km)                                            AS distance,
        AVG(estimated_delivery_hours)                               AS hours,
        SUM(distance_km) / NULLIF(SUM(estimated_delivery_hours), 0) AS speed
    FROM delivery_performance
    {where}
    GROUP BY transport_mode
    ORDER BY speed DESC
    """)

st.dataframe(transport, use_container_width=True)

fig = px.bar(
    transport,
    x="transport_mode",
    y="speed",
    color="transport_mode",
    title="Transport Efficiency (km/hr)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

left, right = st.columns(2)

distance = run_query(f"SELECT distance_km FROM delivery_performance {where}")
fig = px.histogram(
    distance, x="distance_km", nbins=30, title="Route Distance Distribution"
)
left.plotly_chart(fig, use_container_width=True)

route_efficiency = run_query(f"""
    SELECT distance_km, estimated_delivery_hours, transport_mode
    FROM delivery_performance
    {where}
    """)
fig = px.scatter(
    route_efficiency,
    x="distance_km",
    y="estimated_delivery_hours",
    color="transport_mode",
    title="Distance vs Delivery Time",
)
right.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🌍 Longest Routes")

long_routes = run_query(f"""
    SELECT
        route_id, order_id, warehouse_id, transport_mode,
        distance_km, estimated_delivery_hours
    FROM delivery_performance
    {where}
    ORDER BY distance_km DESC
    LIMIT 20
    """)

st.dataframe(long_routes, use_container_width=True, height=400)

st.divider()

st.subheader("🏭 Warehouse Route Volume")

warehouse = run_query(f"""
    SELECT
        w.name,
        COUNT(*)           AS routes,
        AVG(d.distance_km) AS avg_distance
    FROM delivery_performance d
    JOIN warehouses w ON d.warehouse_id = w.warehouse_id
    {get_where(filters, alias="d")}
    GROUP BY w.name
    ORDER BY routes DESC
    """)

fig = px.bar(
    warehouse, x="name", y="routes", color="routes", title="Routes by Warehouse"
)
fig.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🗺 Warehouse Network")

network = run_query("""
    SELECT
        w.name, w.city, w.country, w.latitude, w.longitude,
        COUNT(d.route_id) AS routes
    FROM warehouses w
    LEFT JOIN delivery_performance d ON w.warehouse_id = d.warehouse_id
    GROUP BY w.name, w.city, w.country, w.latitude, w.longitude
    """)

fig = px.scatter_mapbox(
    network,
    lat="latitude",
    lon="longitude",
    size="routes",
    hover_name="name",
    hover_data=["city", "country", "routes"],
    zoom=3.5,
    center={"lat": 50, "lon": 6},
    height=500,
)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)
