"""Customer Analytics page."""

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from queries import get_where, run_query, top_customers
from components.filters import render_filters
from components.sidebar import render_sidebar

st.title("🌍 Customer Analytics")

render_sidebar()
filters = render_filters()

where = get_where(filters)


metrics = run_query(f"""
    SELECT
        COUNT(DISTINCT customer_id) AS customers,
        COUNT(order_id)             AS shipments,
        AVG(package_weight_kg)      AS avg_weight
    FROM delivery_performance
    {where}
    """).iloc[0]

if int(metrics.shipments) == 0:
    st.warning("No customers match the current filters.")
    st.stop()

a, b, c = st.columns(3)
a.metric("Customers", f"{int(metrics.customers):,}")
b.metric("Shipments", f"{int(metrics.shipments):,}")
c.metric("Average Package Weight", f"{metrics.avg_weight:.1f} kg")

st.divider()

left, right = st.columns(2)

countries = run_query(f"""
    SELECT customer_country, COUNT(*) AS shipments
    FROM delivery_performance
    {where}
    GROUP BY customer_country
    ORDER BY shipments DESC
    """)
fig = px.bar(
    countries.head(15),
    x="customer_country",
    y="shipments",
    color="shipments",
    title="Shipments by Country",
)
left.plotly_chart(fig, use_container_width=True)

customers = top_customers(filters)
fig = px.bar(
    customers, x="customer", y="shipments", color="shipments", title="Top Customers"
)
right.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("👥 Customer Shipment Summary")
st.dataframe(customers, use_container_width=True)

st.divider()

st.subheader("📦 Customer Package Behaviour")

package = run_query(f"""
    SELECT
        package_size,
        COUNT(*)               AS shipments,
        AVG(package_weight_kg) AS avg_weight
    FROM delivery_performance
    {where}
    GROUP BY package_size
    ORDER BY shipments DESC
    """)
fig = px.bar(
    package,
    x="package_size",
    y="shipments",
    color="avg_weight",
    title="Package Size Preferences",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🗺 Customer Distribution")

customer_locations = run_query(f"""
    SELECT DISTINCT
        d.customer_id,
        c.first_name, c.last_name, c.city, c.country, c.latitude, c.longitude
    FROM delivery_performance d
    JOIN dim_customers c ON d.customer_id = c.customer_id
    {get_where(filters, alias="d")}
    """)

fig = px.scatter_mapbox(
    customer_locations,
    lat="latitude",
    lon="longitude",
    hover_name="first_name",
    hover_data=["last_name", "city", "country"],
    zoom=3.5,
    center={"lat": 50, "lon": 10},
    height=600,
    opacity=0.7,
)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("📦 Customer Order Status")

status = run_query(f"""
    SELECT status, COUNT(*) AS shipments
    FROM delivery_performance
    {where}
    GROUP BY status
    ORDER BY shipments DESC
    """)
fig = px.pie(
    status, names="status", values="shipments", title="Shipment Status Distribution"
)
st.plotly_chart(fig, use_container_width=True)
