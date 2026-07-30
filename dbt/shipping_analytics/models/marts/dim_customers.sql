{{ config(
    materialized='table'
) }}

select
    customer_id,
    first_name,
    last_name,
    email,
    city,
    state,
    country

from {{ ref('stg_customers') }}