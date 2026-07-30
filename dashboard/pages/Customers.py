import streamlit as st
import plotly.express as px

from database import get_connection
from queries import (
    top_customers,
    run_query
)

from components.sidebar import render_sidebar
from components.filters import render_filters


st.title("🌍 Customer Analytics")

render_sidebar()
render_filters()


con = get_connection()


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
# KPI SECTION
# -------------------------

metrics = run_query("""
SELECT

    COUNT(DISTINCT customer_id)
        AS customers,

    COUNT(order_id)
        AS shipments,

    AVG(package_weight_kg)
        AS avg_weight

FROM fact_shipments

""").iloc[0]


a, b, c = st.columns(3)


a.metric(
    "Customers",
    f"{int(metrics.customers):,}"
)

b.metric(
    "Shipments",
    f"{int(metrics.shipments):,}"
)

c.metric(
    "Average Package Weight",
    f"{metrics.avg_weight:.1f} kg"
)



st.divider()



# -------------------------
# CUSTOMER COUNTRIES
# -------------------------

left, right = st.columns(2)


countries = run_query("""
SELECT

    customer_country,

    COUNT(*) shipments

FROM fact_shipments

GROUP BY customer_country

ORDER BY shipments DESC
""")


fig = px.bar(
    countries.head(15),
    x="customer_country",
    y="shipments",
    color="shipments",
    title="Shipments by Country"
)


left.plotly_chart(
    fig,
    use_container_width=True
)



# -------------------------
# TOP CUSTOMERS
# -------------------------

customers = top_customers(filters)


fig = px.bar(
    customers,
    x="customer",
    y="shipments",
    color="shipments",
    title="Top Customers"
)


right.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# CUSTOMER TABLE
# -------------------------

st.subheader(
    "👥 Customer Shipment Summary"
)


st.dataframe(
    customers,
    use_container_width=True
)



st.divider()



# -------------------------
# PACKAGE PREFERENCES
# -------------------------

st.subheader(
    "📦 Customer Package Behaviour"
)


package = run_query("""
SELECT

    package_size,

    COUNT(*) shipments,

    AVG(package_weight_kg)
        avg_weight

FROM fact_shipments

GROUP BY package_size

ORDER BY shipments DESC

""")


fig = px.bar(
    package,
    x="package_size",
    y="shipments",
    color="avg_weight",
    title="Package Size Preferences"
)


st.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# CUSTOMER MAP
# -------------------------

st.subheader(
    "🗺 Customer Distribution"
)


customer_locations = run_query("""
SELECT

    first_name,

    last_name,

    city,

    country,

    latitude,

    longitude

FROM customers

""")


fig = px.scatter_mapbox(
    customer_locations,
    lat="latitude",
    lon="longitude",
    hover_name="first_name",
    hover_data=[
        "last_name",
        "city",
        "country"
    ],
    zoom=1,
    height=600
)


fig.update_layout(
    mapbox_style="open-street-map"
)


st.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# STATUS BEHAVIOUR
# -------------------------

st.subheader(
    "📦 Customer Order Status"
)


status = run_query("""
SELECT

    status,

    COUNT(*) shipments

FROM fact_shipments

GROUP BY status

ORDER BY shipments DESC

""")


fig = px.pie(
    status,
    names="status",
    values="shipments",
    title="Shipment Status Distribution"
)


st.plotly_chart(
    fig,
    use_container_width=True
)