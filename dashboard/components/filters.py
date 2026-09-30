"""
Sidebar dashboard filters.

Renders warehouse, status, priority, and risk multiselects; exposes
a reset action; and returns the current selection as a dict.
"""

import streamlit as st

from database import get_connection

FILTER_KEYS = (
    "warehouse_filter",
    "status_filter",
    "priority_filter",
    "risk_filter",
)


def initialise_filters() -> None:
    """Ensure all filter keys exist in session state."""
    for key in FILTER_KEYS:
        st.session_state.setdefault(key, [])


def reset_filters() -> None:
    """Clear all filter selections (removes keys, then reruns)."""
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)
    st.rerun()


@st.cache_data(ttl=300)
def _load_filter_options() -> dict[str, list[str]]:
    """Load distinct filter values from the warehouse (cached 5 min)."""
    con = get_connection()

    def values(sql: str) -> list[str]:
        return con.sql(sql).df().iloc[:, 0].tolist()

    return {
        "warehouses": values("SELECT name FROM warehouses ORDER BY name"),
        "statuses": values(
            "SELECT DISTINCT status        FROM delivery_performance ORDER BY status"
        ),
        "priorities": values(
            "SELECT DISTINCT priority      FROM delivery_performance ORDER BY priority"
        ),
        "risks": values(
            "SELECT DISTINCT risk_category FROM delivery_performance ORDER BY risk_category"
        ),
    }


def render_filters() -> dict[str, list[str]]:
    """Render the sidebar filter panel and return the current selection."""
    initialise_filters()

    st.sidebar.subheader("🔎 Dashboard Filters")

    if st.sidebar.button("♻️ Reset Filters"):
        reset_filters()  # calls st.rerun(); nothing below executes

    options = _load_filter_options()

    selected_warehouses = st.sidebar.multiselect(
        "🏭 Warehouse",
        options["warehouses"],
        key="warehouse_filter",
    )
    selected_status = st.sidebar.multiselect(
        "📦 Status",
        options["statuses"],
        key="status_filter",
    )
    selected_priority = st.sidebar.multiselect(
        "🚚 Priority",
        options["priorities"],
        key="priority_filter",
    )
    selected_risk = st.sidebar.multiselect(
        "⚠️ Risk",
        options["risks"],
        key="risk_filter",
    )

    return {
        "warehouses": selected_warehouses,
        "statuses": selected_status,
        "priorities": selected_priority,
        "risk": selected_risk,
    }
