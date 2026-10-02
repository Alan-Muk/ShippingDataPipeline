# Data Dictionary

Every table, every column, every meaning. If you're reading a query and wondering "what is `estimated_delivery_hours` actually?" — this is the answer.

**Contents:**
- [Source tables (DuckDB)](#source-tables-duckdb)
- [dbt staging models](#dbt-staging-models)
- [dbt mart models](#dbt-mart-models)
- [Computed fields](#computed-fields)
- [Constants and thresholds](#constants-and-thresholds)

---

## Source tables (DuckDB)

These tables are created by the Python pipeline and loaded directly into DuckDB. They are the raw material for dbt.

### `customers`

100 synthetic EU customers across 30 cities in 17 countries.

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| `customer_id` | STRING | UUID, stable per customer | `uuid.uuid4()` |
| `title` | STRING | Mr / Ms / Mrs / Dr | Synthetic |
| `first_name` | STRING | Given name | Synthetic |
| `last_name` | STRING | Family name | Synthetic |
| `gender` | STRING | male / female | Synthetic |
| `email` | STRING | `first.last@example.eu` | Synthetic |
| `phone` | STRING | E.164-ish format | Synthetic |
| `street_number` | INTEGER | 1–250 | Synthetic |
| `street_name` | STRING | e.g. "Main Street" | Synthetic |
| `city` | STRING | From `EU_CITIES` | Synthetic |
| `state` | STRING | Region / province | Synthetic |
| `country` | STRING | EU country | Synthetic |
| `postcode` | STRING | Digits, country-agnostic | Synthetic |
| `latitude` | FLOAT | WGS84 latitude, jittered ±0.25° | Synthetic |
| `longitude` | FLOAT | WGS84 longitude, jittered ±0.25° | Synthetic |
| `registered_date` | STRING | ISO-8601 timestamp | Synthetic |
| `nationality` | STRING | 2-letter country code | Derived from country |

**Note:** no `title`/`first_name`/`last_name` nulls. No duplicate `customer_id`s. Both are enforced by the generator's construction and tested in `tests/test_customers.py`.

---

### `warehouses`

4 static reference warehouses. **Not generated per-run** — they're fixed data.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `warehouse_id` | STRING | `WH-XXX` | `WH-001` |
| `name` | STRING | Human-readable name | "Amsterdam Distribution Centre" |
| `city` | STRING | City | "Amsterdam" |
| `country` | STRING | Country | "Netherlands" |
| `latitude` | FLOAT | WGS84 latitude | 52.3676 |
| `longitude` | FLOAT | WGS84 longitude | 4.9041 |
| `capacity` | INTEGER | Storage units (pallets) | 500 |

**The 4 warehouses:**
1. Amsterdam Distribution Centre — Netherlands
2. Berlin Fulfilment Hub — Germany
3. Paris Logistics Centre — France
4. Madrid Shipping Hub — Spain

**Capacity values are relative**, not absolute. They're sized so that shipments represent ~15% utilisation, which makes the dashboard's capacity chart meaningful.

---

### `weather`

One row per warehouse, from the latest Open-Meteo observation.

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| `warehouse_id` | STRING | FK to `warehouses` | Warehouse |
| `timestamp` | TIMESTAMP | Observation time | `datetime.now()` |
| `temperature` | FLOAT | °C | Open-Meteo |
| `wind_speed` | FLOAT | km/h | Open-Meteo |

**Only the latest observation per warehouse is kept.** If you want weather history, the bronze JSON files preserve every fetch.

---

### `orders`

300 synthetic orders — 3 per customer.

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `order_id` | STRING | UUID | — |
| `customer_id` | STRING | FK to `customers` | — |
| `warehouse_id` | STRING | FK to `warehouses` | — |
| `package_weight_kg` | FLOAT | Package weight | 0.5 – 25.0 |
| `package_size` | STRING | small / medium / large | — |
| `priority` | STRING | standard / express / priority | — |
| `status` | STRING | created / processing / shipped / delivered / cancelled | — |
| `created_at` | TIMESTAMP | Order placement time | last 90 days |

**Distributions:**
- Weights are uniform on `[0.5, 25.0]`, rounded to 2 decimals
- Status, priority, and size are uniform random choices

---

### `routes`

One route per order. Computed from haversine distance between warehouse and customer coordinates.

| Column | Type | Description | Derivation |
|--------|------|-------------|------------|
| `route_id` | STRING | `RT-{order_id}` | `pl.concat_str(["RT-", order_id])` |
| `order_id` | STRING | FK to `orders` | 1:1 with orders |
| `customer_id` | STRING | FK to `customers` | From order |
| `warehouse_id` | STRING | FK to `warehouses` | From order |
| `distance_km` | FLOAT | Great-circle distance | Haversine formula |
| `estimated_hours` | FLOAT | Delivery time estimate | Mode-specific speed + handling |
| `transport_mode` | STRING | van / truck / air | Distance-based assignment |

**Transport mode thresholds:**

| Distance | Mode | Speed | Handling |
|----------|------|-------|----------|
| `< 500 km` | `van` | 70 km/h | +1h |
| `500–3,000 km` | `truck` | 55 km/h | +2h |
| `≥ 3,000 km` | `air` | 800 km/h | +12h |

**Why vans are faster than trucks:** vans handle smaller loads, do less load-balancing, and avoid heavy-vehicle routing. 70 vs 55 km/h reflects typical European logistics.

**Notable:** intra-EU routes never reach 3,000 km, so `transport_mode = 'air'` is rare by design. It's a physical constraint, not a bug.

---

### `delivery_risk`

One risk score per route.

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `route_id` | STRING | FK to `routes` | — |
| `order_id` | STRING | FK to `orders` | — |
| `warehouse_id` | STRING | FK to `warehouses` | — |
| `distance_km` | FLOAT | Copied from route | — |
| `estimated_hours` | FLOAT | Copied from route | — |
| `temperature` | FLOAT | Copied from weather | — |
| `wind_speed` | FLOAT | Copied from weather | — |
| `risk_score` | INTEGER | 0–100 | — |
| `risk_level` | STRING | LOW / MEDIUM / HIGH / CRITICAL | Derived from score |

**Risk level thresholds:**

| Score | Level |
|-------|-------|
| `≥ 75` | CRITICAL |
| `50–74` | HIGH |
| `25–49` | MEDIUM |
| `0–24` | LOW |

---

## dbt staging models

Staging models are **views**. They clean and standardize source data.

### `stg_customers`

Selects and passes through customer attributes.

```sql
select
    customer_id, first_name, last_name, email,
    city, state, country, latitude, longitude
from {{ source('shipping', 'customers') }}
```

**Columns:** same as source, subset of columns.

---

### `stg_orders`

Selects and passes through order attributes.

```sql
select
    order_id, customer_id, warehouse_id,
    package_weight_kg, package_size, priority, status, created_at
from {{ source('shipping', 'orders') }}
```

**Columns:** same as source, subset.

---

## dbt mart models

Marts are **tables**. They contain business logic.

### `dim_customers`

Customer dimension — one row per customer.

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | STRING | Primary key |
| `first_name` | STRING | |
| `last_name` | STRING | |
| `email` | STRING | |
| `city` | STRING | |
| `state` | STRING | |
| `country` | STRING | |
| `latitude` | FLOAT | For mapping |
| `longitude` | FLOAT | For mapping |

**Tests:** `unique`, `not_null` on `customer_id`; `not_null` on `country`.

---

### `fact_shipments`

Shipment fact table — one row per order.

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | STRING | Primary key |
| `customer_id` | STRING | FK to `dim_customers` |
| `warehouse_id` | STRING | FK to `warehouses` |
| `order_date` | TIMESTAMP | Renamed from `created_at` |
| `package_weight_kg` | FLOAT | |
| `package_size` | STRING | |
| `priority` | STRING | |
| `status` | STRING | |
| `customer_city` | STRING | Denormalized |
| `customer_country` | STRING | Denormalized |

**Tests:** `unique`, `not_null` on `order_id`; `not_null` on `customer_id`, `warehouse_id`; `relationships` on `customer_id → dim_customers`; `accepted_values` on `status`.

---

### `delivery_performance`

The "answer" table. One row per order, enriched with route, weather, and risk.

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| `order_id` | STRING | Primary key | fact |
| `customer_id` | STRING | | fact |
| `warehouse_id` | STRING | | fact |
| `order_date` | TIMESTAMP | | fact |
| `status` | STRING | | fact |
| `package_weight_kg` | FLOAT | | fact |
| `package_size` | STRING | | fact |
| `priority` | STRING | | fact |
| `customer_city` | STRING | | fact |
| `customer_country` | STRING | | fact |
| `route_id` | STRING | | routes |
| `distance_km` | FLOAT | | routes |
| `estimated_delivery_hours` | FLOAT | Renamed from `estimated_hours` | routes |
| `transport_mode` | STRING | | routes |
| `temperature` | FLOAT | | delivery_risk |
| `wind_speed` | FLOAT | | delivery_risk |
| `risk_score` | INTEGER | | delivery_risk |
| `risk_category` | STRING | Renamed from `risk_level` | delivery_risk |

**Tests:** `unique`, `not_null` on `order_id`; `not_null` on `customer_id`, `warehouse_id`, `risk_score`; `accepted_values` on `transport_mode`, `risk_category`.

**Why the renames?**
- `estimated_hours` → `estimated_delivery_hours` — more explicit in a dashboard context
- `risk_level` → `risk_category` — matches the API the dashboard exposes

---

## Computed fields

### Distance (haversine)

Great-circle distance between two coordinates on a sphere of radius 6,371 km.

```
a = sin²(Δφ/2) + cos(φ₁) · cos(φ₂) · sin²(Δλ/2)
c = 2 · atan2(√a, √(1−a))
d = R · c
```

Implemented vectorized in `src/transform/routes.py:_haversine_expr`.

**Accuracy:** ±0.5% for distances under 5,000 km, which is well within the tolerance needed for analytics.

### Risk score

Sum of points from four factors:

| Factor | Tiers (value → points) |
|--------|------------------------|
| Distance | `> 2,000 km → 15`, `> 5,000 km → 25`, `> 10,000 km → 35` |
| Duration | `> 12 h → 5`, `> 24 h → 15`, `> 36 h → 25` |
| Temperature | `> 20 °C → 10`, `> 25 °C → 20` |
| Wind | `> 5 km/h → 5`, `> 10 km/h → 15` |

**Cap:** 100. **Unknown weather penalty:** 15.

Each factor contributes independently. The highest matching tier in each factor applies.

**Why these thresholds?** They were tuned so a natural EU logistics dataset produces roughly:
- ~55% LOW
- ~40% MEDIUM
- ~5% HIGH + CRITICAL

That distribution is what real operational risk looks like — most shipments are fine, a few are not.

### Transport mode

Deterministic assignment based on `distance_km`:

```python
(0.0, "van")       # < 500 km
(500.0, "truck")   # 500–2,999 km
(3_000.0, "air")   # ≥ 3,000 km
```

### Estimated hours

```python
hours = distance_km / SPEED[mode] + HANDLING_HOURS[mode]
```

Where `SPEED = {van: 70, truck: 55, air: 800}` and `HANDLING_HOURS = {van: 1, truck: 2, air: 12}`.

---

## Constants and thresholds

All tunable values live in code, not in queries.

### `src/config/settings.py`

| Constant | Value | Purpose |
|----------|-------|---------|
| `DEFAULT_CUSTOMER_COUNT` | 100 | Customers per run |
| `DEFAULT_WAREHOUSE_COUNT` | 4 | Warehouses generated |
| `DEFAULT_ORDERS_PER_CUSTOMER` | 3 | Orders per customer |
| `PIPELINE_SEED` | `None` | Set to int for reproducibility |

### `src/transform/routes.py`

| Constant | Purpose |
|----------|---------|
| `EARTH_RADIUS_KM` | 6,371.0 |
| `MODE_DISTANCE_TIERS` | van/truck/air thresholds |
| `TRANSPORT_SPEEDS_KMH` | `{van: 70, truck: 55, air: 800}` |
| `HANDLING_HOURS` | `{van: 1, truck: 2, air: 12}` |

### `src/transform/delivery_risk.py`

| Constant | Purpose |
|----------|---------|
| `DISTANCE_TIERS_KM` | Distance risk points |
| `DURATION_TIERS_H` | Duration risk points |
| `TEMPERATURE_TIERS_C` | Temperature risk points |
| `WIND_TIERS_KMH` | Wind risk points |
| `UNKNOWN_WEATHER_PENALTY` | Points for missing weather |
| `RISK_LEVELS` | Level boundaries |

### `src/extract/customers.py`

| Constant | Value | Purpose |
|----------|-------|---------|
| `EU_CITIES` | 30 entries | (city, state, country, lat, lon) tuples |
| `GENDERS` | 2 | male / female |
| `FIRST_NAMES` | 24 (12 per gender) | Realistic European names |
| `LAST_NAMES` | 22 | Pan-European surnames |

---

## See also

- [Architecture](architecture.md) — why the layers exist
- [`src/README.md`](../src/README.md) — backend module reference
- [`dbt/shipping_analytics/README.md`](../dbt/shipping_analytics/README.md) — dbt model docs