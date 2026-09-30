{{ config(materialized='table') }}

select
    f.order_id,
    f.customer_id,
    f.warehouse_id,

    f.order_date,
    f.status,

    f.package_weight_kg,
    f.package_size,
    f.priority,

    -- Customer geography (from fact_shipments)
    f.customer_city,
    f.customer_country,

    -- Route attributes
    r.route_id,
    r.distance_km,
    r.estimated_hours as estimated_delivery_hours,
    r.transport_mode,

    -- Weather
    dr.temperature,
    dr.wind_speed,

    -- Risk
    dr.risk_score,
    dr.risk_level as risk_category

from {{ ref('fact_shipments') }} f
left join {{ source('shipping', 'routes') }} r on f.order_id = r.order_id
left join
    {{ source('shipping', 'delivery_risk') }} dr
    on f.order_id = dr.order_id
