import streamlit as st

from queries import overview_metrics
from components.filters import render_filters


st.set_page_config(
    page_title="Shipping Analytics",
    page_icon="🚚",
    layout="wide"
)


# -------------------------
# HEADER
# -------------------------

from components.header import render_header

render_header()


st.markdown("""
### End-to-end logistics intelligence platform

Explore shipment performance, delivery risk, route efficiency,
warehouse operations, and customer behaviour through interactive
analytics dashboards.

This platform simulates a modern logistics data environment built
using a production-style analytics stack.
""")


st.divider()

from components.sidebar import render_sidebar


render_sidebar()

render_filters()


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


active_filters = sum(
    [
        len(filters["warehouses"]),
        len(filters["statuses"]),
        len(filters["priorities"]),
        len(filters["risk"])
    ]
)


if active_filters:

    st.sidebar.info(
        f"🎯 Active filters: {active_filters}"
    )

else:

    st.sidebar.success(
        "Showing all data"
    )

# -------------------------
# LIVE METRICS
# -------------------------

st.subheader("📊 Platform Overview")


metrics = overview_metrics(filters).iloc[0]


a, b, c, d = st.columns(4)


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


st.divider()


# -------------------------
# WHAT YOU CAN EXPLORE
# -------------------------

st.subheader("🔎 Explore Analytics")


from components.cards import dashboard_card


col1, col2 = st.columns(2)


with col1:

    dashboard_card(
        "Executive Overview",
        "Monitor shipment volume, delivery status, operational KPIs and business performance.",
        "📊"
    )


    dashboard_card(
        "Route Analytics",
        "Analyse transport modes, route distance, efficiency and delivery estimates.",
        "🚛"
    )


with col2:

    dashboard_card(
        "Delivery Risk",
        "Identify risky shipments using route distance and weather conditions.",
        "⚠️"
    )


    dashboard_card(
        "Warehouse Analytics",
        "Compare warehouse performance, capacity and geographic distribution.",
        "🏭"
    )

st.divider()


# -------------------------
# ARCHITECTURE
# -------------------------

st.subheader("🏗 Data Platform Architecture")


st.code("""
External Data Sources
          |
          v
Python ETL Pipeline
          |
          v
Bronze Layer
Raw JSON Data
          |
          v
Silver Layer
Clean Parquet Data
          |
          v
DuckDB Analytics Warehouse
          |
          v
dbt Transformations
          |
          v
Streamlit BI Dashboards
""")


st.divider()


# -------------------------
# TECHNOLOGY STACK
# -------------------------

st.subheader("⚙️ Technology Stack")


tech = {
    "Data Processing": "Python + Polars",
    "Storage": "Parquet Data Lake",
    "Warehouse": "DuckDB",
    "Transformation": "dbt",
    "Testing": "pytest + dbt tests",
    "Orchestration": "Airflow",
    "Visualisation": "Streamlit",
    "Containers": "Podman",
}


for key, value in tech.items():

    st.write(
        f"**{key}:** {value}"
    )


st.divider()


st.success(
    "Use the navigation menu on the left to explore the analytics dashboards."
)



