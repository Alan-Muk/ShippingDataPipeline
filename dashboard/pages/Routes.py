import streamlit as st
import plotly.express as px

from queries import run_query

from components.sidebar import render_sidebar
from components.filters import render_filters


st.title("🚛 Route Analytics")

render_sidebar()
render_filters()



# -------------------------
# GLOBAL FILTERS
# -------------------------

filters = {

    "warehouses":
        st.session_state.get(
            "warehouse_filter",
            []
        ),

    "statuses":
        st.session_state.get(
            "status_filter",
            []
        ),

    "priorities":
        st.session_state.get(
            "priority_filter",
            []
        ),

    "risk":
        st.session_state.get(
            "risk_filter",
            []
        )
}



# -------------------------
# KPI SECTION
# -------------------------

metrics = run_query("""
SELECT

    COUNT(*) AS routes,

    AVG(distance_km) AS avg_distance,

    AVG(estimated_hours) AS avg_hours,

    AVG(distance_km / estimated_hours)
        AS avg_speed

FROM routes

""").iloc[0]



a, b, c, d = st.columns(4)


a.metric(
    "Total Routes",
    f"{int(metrics.routes):,}"
)

b.metric(
    "Average Distance",
    f"{metrics.avg_distance:,.0f} km"
)

c.metric(
    "Average Delivery Time",
    f"{metrics.avg_hours:.1f} hrs"
)

d.metric(
    "Average Speed",
    f"{metrics.avg_speed:.1f} km/hr"
)



st.divider()



# -------------------------
# TRANSPORT PERFORMANCE
# -------------------------

st.subheader(
    "🚚 Transport Performance"
)


transport = run_query("""
SELECT

    transport_mode,

    COUNT(*) AS shipments,

    AVG(distance_km) AS distance,

    AVG(estimated_hours) AS hours,

    AVG(distance_km / estimated_hours)
        AS speed

FROM routes

GROUP BY transport_mode

ORDER BY speed DESC

""")


st.dataframe(
    transport,
    use_container_width=True
)



fig = px.bar(
    transport,
    x="transport_mode",
    y="speed",
    color="transport_mode",
    title="Transport Efficiency (km/hr)"
)


st.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# DISTANCE ANALYSIS
# -------------------------

left, right = st.columns(2)



distance = run_query("""
SELECT

    distance_km

FROM routes

""")


fig = px.histogram(
    distance,
    x="distance_km",
    nbins=30,
    title="Route Distance Distribution"
)


left.plotly_chart(
    fig,
    use_container_width=True
)



# -------------------------
# ROUTE TIME VS DISTANCE
# -------------------------

route_efficiency = run_query("""
SELECT

    distance_km,

    estimated_hours,

    transport_mode

FROM routes

""")


fig = px.scatter(
    route_efficiency,
    x="distance_km",
    y="estimated_hours",
    color="transport_mode",
    title="Distance vs Delivery Time"
)


right.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# LONGEST ROUTES
# -------------------------

st.subheader(
    "🌍 Longest Routes"
)


long_routes = run_query("""
SELECT

    route_id,

    warehouse_id,

    transport_mode,

    distance_km,

    estimated_hours

FROM routes

ORDER BY distance_km DESC

LIMIT 20

""")


st.dataframe(
    long_routes,
    use_container_width=True
)



st.divider()



# -------------------------
# WAREHOUSE ROUTE VOLUME
# -------------------------

st.subheader(
    "🏭 Warehouse Route Volume"
)


warehouse = run_query("""
SELECT

    warehouse_id,

    COUNT(*) AS routes,

    AVG(distance_km) AS avg_distance

FROM routes

GROUP BY warehouse_id

ORDER BY routes DESC

""")


fig = px.bar(
    warehouse,
    x="warehouse_id",
    y="routes",
    color="warehouse_id",
    title="Routes by Warehouse"
)


st.plotly_chart(
    fig,
    use_container_width=True
)



st.divider()



# -------------------------
# TRANSPORT MAP VIEW
# -------------------------

st.subheader(
    "🗺 Warehouse Network"
)


network = run_query("""
SELECT

    w.name,

    w.city,

    w.country,

    w.latitude,

    w.longitude,

    COUNT(r.route_id) AS routes

FROM warehouses w

LEFT JOIN routes r

ON w.warehouse_id = r.warehouse_id

GROUP BY

    w.name,

    w.city,

    w.country,

    w.latitude,

    w.longitude

""")


fig = px.scatter_mapbox(
    network,
    lat="latitude",
    lon="longitude",
    size="routes",
    hover_name="name",
    hover_data=[
        "city",
        "country",
        "routes"
    ],
    zoom=3,
    height=500
)


fig.update_layout(
    mapbox_style="open-street-map"
)


st.plotly_chart(
    fig,
    use_container_width=True
)