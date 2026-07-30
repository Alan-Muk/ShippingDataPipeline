import streamlit as st
from pathlib import Path


def render_header():

    logo = Path(__file__).parent.parent / "assets" / "logo.png"

    col1, col2 = st.columns(
        [1, 5]
    )


    with col1:

        if logo.exists():

            st.image(
                str(logo),
                width=90
            )


    with col2:

        st.markdown(
            """
            # 🚚 Shipping Analytics Platform
            
            #### Logistics intelligence powered by Python, DuckDB and dbt
            """
        )


    st.divider()