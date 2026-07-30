{{ config(
    materialized='table'
) }}

select
    f.order_id,
    f.customer_id,
    f.warehouse_id,

    f.order_date,
    f.status,

    f.package_weight_kg,
    f.package_size,
    f.priority,

    r.distance_km,
    r.estimated_hours as estimated_delivery_hours,

    w.temperature,
    w.wind_speed,

    dr.risk_score,
    dr.risk_level as risk_category

from {{ ref('fact_shipments') }} f

left join {{ source('shipping', 'routes') }} r
    on f.order_id = r.order_id

left join {{ source('shipping', 'weather') }} w
    on f.warehouse_id = w.warehouse_id

left join {{ source('shipping', 'delivery_risk') }} dr
    on f.order_id = dr.order_id