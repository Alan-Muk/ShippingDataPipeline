from pathlib import Path

import duckdb
import streamlit as st


DB_PATH = (
    Path(__file__).parent.parent
    / "warehouse"
    / "shipping.duckdb"
)


@st.cache_resource
def get_connection():

    return duckdb.connect(
        str(DB_PATH),
        read_only=True
    )


@st.cache_data
def query(sql):

    con = get_connection()

    return con.execute(sql).df()