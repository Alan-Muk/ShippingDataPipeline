import streamlit as st


def dashboard_card(title, description, icon):
    st.markdown(
        f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:12px;
            border:1px solid #E5E7EB;
            height:180px;
        ">

        <h3>
        {icon} {title}
        </h3>

        <p>
        {description}
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )
