"""Shipping Analytics — landing page."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from components.cards import CARD_CSS, dashboard_card
from components.filters import render_filters
from components.header import render_header
from components.sidebar import render_sidebar
from queries import overview_metrics

st.set_page_config(
    page_title="Shipping Analytics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CARD_CSS, unsafe_allow_html=True)

render_header()

st.markdown("""
### End-to-end logistics intelligence platform

Explore shipment performance, delivery risk, route efficiency,
warehouse operations, and customer behaviour through interactive
analytics dashboards.

This platform simulates a modern European logistics operation:
**100 synthetic customers**, **4 warehouses**, **300 shipments**,
and a **4-tier delivery risk model** — all built with a
production-style analytics stack.
""")

st.divider()

render_sidebar()
filters = render_filters()

active_filters = sum(len(v) for v in filters.values())

if active_filters:
    st.sidebar.info(f"🎯 Active filters: {active_filters}")
else:
    st.sidebar.success("Showing all data")

st.subheader("📊 Platform Overview")

try:
    metrics_df = overview_metrics(filters)
except Exception as exc:
    st.error(f"Failed to load data: {exc}")
    st.info("Run `python -m src.pipeline` to generate data, then refresh.")
    st.stop()

if metrics_df is None or len(metrics_df) == 0:
    st.warning("No data matches the current filters.")
    st.stop()

metrics = metrics_df.iloc[0]

a, b, c, d = st.columns(4)
a.metric("Shipments", f"{int(metrics.shipments):,}")
b.metric("Customers", f"{int(metrics.customers):,}")
c.metric("Warehouses", f"{int(metrics.warehouses):,}")
d.metric("Average Risk", f"{metrics.avg_risk:.1f}")

st.divider()

st.subheader("🔎 Explore Analytics")

col1, col2 = st.columns(2)

with col1:
    dashboard_card(
        "Executive Overview",
        "Monitor shipment volume, delivery status, operational KPIs and business performance.",
        "📊",
        href="/Overview",
    )
    dashboard_card(
        "Route Analytics",
        "Analyse transport modes, route distance, efficiency and delivery estimates.",
        "🚛",
        href="/Routes",
    )

with col2:
    dashboard_card(
        "Delivery Risk",
        "Identify risky shipments using route distance and weather conditions.",
        "⚠️",
        href="/Risk",
    )
    dashboard_card(
        "Warehouse Analytics",
        "Compare warehouse performance, capacity and geographic distribution.",
        "🏭",
        href="/Warehouses",
    )

st.divider()

st.subheader("🏗 Data Platform Architecture")

st.code(
    """
External Data Sources (synthetic + Open-Meteo)
              │
              ▼
       Python ETL Pipeline
              │
              ▼
   Bronze ──► Silver ──► Gold
   (JSON)    (Parquet)  (routes, risk)
              │
              ▼
      DuckDB Warehouse
              │
              ▼
    dbt (staging → marts)
              │
              ▼
    Streamlit Dashboards
""",
    language="text",
)

st.divider()

st.subheader("⚙️ Technology Stack")

tech = {
    "Language": "Python 3.14",
    "Data Processing": "Polars",
    "Storage": "Parquet data lake (bronze / silver / gold)",
    "Warehouse": "DuckDB",
    "Transformation": "dbt",
    "Testing": "pytest + dbt tests (17 passing)",
    "Visualisation": "Streamlit",
    "Containers": "Podman",
}

for key, value in tech.items():
    st.write(f"**{key}:** {value}")

st.divider()

st.caption("Use the navigation menu on the left to explore the analytics dashboards.")
