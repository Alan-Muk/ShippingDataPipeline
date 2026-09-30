"""Reusable card component for dashboard navigation."""

import streamlit as st


def dashboard_card(
    title: str,
    description: str,
    icon: str,
    href: str | None = None,
) -> None:
    """Render a dashboard card. If `href` is set, the card links to it."""
    wrapper_open = (
        f'<a href="{href}" target="_self" style="text-decoration:none;color:inherit;">'
        if href
        else ""
    )
    wrapper_close = "</a>" if href else ""

    st.markdown(
        f"""
        {wrapper_open}
        <div class="dashboard-card">
            <h3 style="margin-top:0;">{icon} {title}</h3>
            <p style="margin-bottom:0;opacity:0.85;">{description}</p>
        </div>
        {wrapper_close}
        """,
        unsafe_allow_html=True,
    )


CARD_CSS = """
<style>
.dashboard-card {
    background: var(--secondary-background-color);
    color: var(--text-color);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid var(--secondary-background-color);
    min-height: 180px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.dashboard-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
a:hover .dashboard-card {
    border-color: var(--primary-color);
}
</style>
"""
