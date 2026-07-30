{{ config(
    materialized='table'
) }}

select
    o.order_id,
    o.customer_id,
    o.warehouse_id,

    o.created_at as order_date,

    o.package_weight_kg,
    o.package_size,
    o.priority,
    o.status,

    c.city as customer_city,
    c.country as customer_country

from {{ ref('stg_orders') }} o

left join {{ ref('stg_customers') }} c
    on o.customer_id = c.customer_id