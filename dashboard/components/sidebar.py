import streamlit as st


def render_sidebar():

    st.sidebar.title(
        "🚚 Shipping Analytics"
    )


    st.sidebar.markdown(
        """
        ---
        
        **Data Platform**

        🐍 Python ETL  
        🐻 DuckDB Warehouse  
        🔧 dbt Models  
        📦 Parquet Lake  
        📈 Streamlit BI
        
        ---
        
        **Environment**

        Fedora Silverblue  
        Podman Containers
        
        """
    )