import streamlit as st

from database import get_connection


def initialise_filters():
    defaults = {
        "warehouse_filter": [],
        "status_filter": [],
        "priority_filter": [],
        "risk_filter": [],
        "date_filter": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_filters():
    st.session_state.warehouse_filter = []
    st.session_state.status_filter = []
    st.session_state.priority_filter = []
    st.session_state.risk_filter = []
    st.session_state.date_filter = []


def render_filters():
    initialise_filters()

    con = get_connection()

    st.sidebar.subheader("🔎 Dashboard Filters")

    if st.sidebar.button("♻️ Reset Filters"):
        reset_filters()

    warehouses = (
        con.sql(
            """
        SELECT
            name
        FROM warehouses
        ORDER BY name
    """
        )
        .df()["name"]
        .tolist()
    )

    selected_warehouses = st.sidebar.multiselect(
        "🏭 Warehouse", warehouses, key="warehouse_filter"
    )

    statuses = (
        con.sql(
            """
        SELECT DISTINCT
            status
        FROM delivery_performance
        ORDER BY status
    """
        )
        .df()["status"]
        .tolist()
    )

    selected_status = st.sidebar.multiselect("📦 Status", statuses, key="status_filter")

    priorities = (
        con.sql(
            """
        SELECT DISTINCT
            priority
        FROM delivery_performance
        ORDER BY priority
    """
        )
        .df()["priority"]
        .tolist()
    )

    selected_priority = st.sidebar.multiselect(
        "🚚 Priority", priorities, key="priority_filter"
    )

    risks = (
        con.sql(
            """
        SELECT DISTINCT
            risk_category
        FROM delivery_performance
        ORDER BY risk_category
    """
        )
        .df()["risk_category"]
        .tolist()
    )

    selected_risk = st.sidebar.multiselect("⚠️ Risk", risks, key="risk_filter")

    return {
        "warehouses": selected_warehouses,
        "statuses": selected_status,
        "priorities": selected_priority,
        "risk": selected_risk,
    }
