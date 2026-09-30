{{ config(materialized='table') }}

select
    customer_id,
    first_name,
    last_name,
    email,
    city,
    state,
    country,
    latitude,
    longitude
from {{ ref('stg_customers') }}
