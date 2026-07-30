SELECT
    order_id,
    customer_id,
    warehouse_id,
    package_weight_kg,
    package_size,
    priority,
    status,
    created_at

FROM {{ source('shipping', 'orders') }}