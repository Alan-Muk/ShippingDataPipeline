"""
Dashboard header component.
"""

from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"


def render_header(
    title: str = "🚚 Shipping Analytics Platform",
    subtitle: str = "Logistics intelligence powered by Python, DuckDB and dbt",
) -> None:
    """Render the dashboard header."""
    col1, col2 = st.columns([1, 5])

    with col1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=90)
        else:
            st.markdown("## 🚚")

    with col2:
        st.markdown(f"# {title}\n\n#### {subtitle}")

    st.divider()
