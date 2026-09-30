"""
Sidebar component.
"""

import streamlit as st

from theme import PAGES


def render_sidebar() -> None:
    """Render the sidebar title, nav links, and stack info."""
    st.sidebar.title("🚚 Shipping Analytics")

    st.sidebar.markdown("#### Navigation")
    for path, label, icon in PAGES:
        st.sidebar.page_link(path, label=label, icon=icon)

    st.sidebar.markdown("""
        ---

        **Data Platform**

        🐍 Python ETL
        🦆 DuckDB Warehouse
        🔧 dbt Models
        📦 Parquet Lake
        📈 Streamlit BI

        ---

        **Stack**

        Python 3.14 · DuckDB · dbt · Polars
        """)
