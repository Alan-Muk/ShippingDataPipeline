# 🚚 Shipping Analytics Data Platform

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python)
![Polars](https://img.shields.io/badge/Polars-Data%20Processing-CD792C)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics%20Warehouse-FFF000?logo=duckdb)
![dbt](https://img.shields.io/badge/dbt-Analytics%20Engineering-FF694B?logo=dbt)
![Streamlit](https://img.shields.io/badge/Streamlit-BI%20Dashboard-FF4B4B?logo=streamlit)
![Airflow](https://img.shields.io/badge/Airflow-Orchestration-017CEE?logo=apacheairflow)
![Podman](https://img.shields.io/badge/Podman-Containerized-892CA0?logo=podman)
![License](https://img.shields.io/badge/License-MIT-green)

An end-to-end data engineering and analytics platform that simulates a modern logistics operation.

The platform ingests customer, warehouse, order, route, and weather data, processes it through a medallion architecture, models analytics datasets using dbt, stores analytical data in DuckDB, and provides interactive business intelligence dashboards through Streamlit.

The project demonstrates a production-style analytics stack:

- Python ETL pipeline
- Polars data processing
- Parquet data lake
- DuckDB analytical warehouse
- dbt transformations
- Data quality testing
- Streamlit BI dashboards
- Apache Superset compatibility
- Containerised services using Podman
- Analytics engineering practices

---

# Overview

Shipping Analytics Data Platform is an automated data processing and analytics system designed to transform raw logistics data into business intelligence insights.

The pipeline workflow:

```text
External Data Sources

          |
          ↓

Python Extraction Layer

          |
          ↓

Bronze Layer
Raw JSON Data

          |
          ↓

Silver Layer
Clean Parquet Data

          |
          ↓

DuckDB Analytics Warehouse

          |
          ↓

dbt Transformation Layer

          |
          ↓

Analytics Marts

          |
          ↓

Streamlit Dashboard

          |
          ↓

Business Intelligence Insights
```

The project follows modern data engineering principles by separating ingestion, transformation, modelling, and analytics responsibilities.

---

# Problem

Logistics operations generate large amounts of operational data that require processing before meaningful analytics can be performed.

A production analytics workflow needs to handle:

- Multiple external data sources
- Data quality management
- Historical data preservation
- Analytical modelling
- Business reporting
- Automated execution

This project explores how raw logistics data can be transformed into reliable analytics datasets.

---

# Architecture

## System Architecture

```text
              External Data Sources

                       |
                       ↓

              Python Extraction Layer

                       |
                       ↓

                 Bronze Layer
                 Raw JSON Files

                       |
                       ↓

                 Silver Layer
              Clean Parquet Data

                       |
                       ↓

              DuckDB Warehouse

                       |
                       ↓

                 dbt Models

                       |
                       ↓

              Analytics Marts

                       |
                       ↓

          Streamlit Analytics Platform
```

---

# Components

## Data Ingestion Layer

Responsible for extracting operational data from source systems.

Responsibilities:

- Collect customer information
- Generate warehouse data
- Retrieve weather observations
- Create shipment records
- Preserve raw ingestion files

Features:

- Timestamped ingestion files
- Reproducible processing
- Historical data preservation

---

## Bronze Data Lake Layer

The bronze layer stores raw source data before transformation.

Example:

```text
data/bronze/

├── customers/

│   └── customers_20260729_094104.json

└── weather/
```

Benefits:

- Preserve original data
- Enable pipeline replay
- Support debugging
- Maintain ingestion history

---

## Silver Transformation Layer

The silver layer contains cleaned and structured Parquet datasets.

Example:

```text
data/silver/customers/customers.parquet
```

Datasets:

| Dataset | Description |
|---|---|
| customers | Clean customer records |
| orders | Shipment order information |
| warehouses | Warehouse locations |
| weather | Weather observations |

Responsibilities:

- Schema standardisation
- Data cleaning
- Type conversion
- Analytics preparation

---

## Gold Analytics Layer

The gold layer contains business-ready datasets.

Examples:

```text
data/gold/routes/routes.parquet

data/gold/delivery_risk/delivery_risk.parquet
```

Contains:

- Route calculations
- Transport information
- Estimated delivery times
- Delivery risk scoring
- Weather impact analysis

---

## Database Warehouse Layer

DuckDB provides analytical warehouse capabilities.

Warehouse location:

```text
warehouse/shipping.duckdb
```

Analytical tables:

```text
customers

orders

warehouses

weather

routes

delivery_risk

stg_customers

stg_orders

dim_customers

fact_shipments

delivery_performance
```

---

## dbt Analytics Layer

dbt transforms warehouse data into analytics-ready models.

Location:

```text
dbt/shipping_analytics/
```

---

# dbt Models

## Staging Models

Location:

```text
models/staging/
```

Models:

- stg_customers
- stg_orders

Purpose:

- Standardise schemas
- Clean source data
- Prepare downstream models

---

## Analytics Models

Location:

```text
models/marts/
```

---

## dim_customers

Customer dimension model.

Columns:

```text
customer_id
first_name
last_name
email
city
state
country
```

---

## fact_shipments

Shipment fact model.

Columns:

```text
order_id
customer_id
warehouse_id
order_date
package_weight_kg
package_size
priority
status
customer_city
customer_country
```

---

## delivery_performance

Final analytics model combining shipment, route, weather, and risk data.

Columns:

```text
order_id
customer_id
warehouse_id
order_date
status
package_weight_kg
package_size
priority
distance_km
estimated_delivery_hours
temperature
wind_speed
risk_score
risk_category
```

---

# Streamlit Analytics Platform

The dashboard provides interactive logistics intelligence.

Run:

```bash
streamlit run dashboard/app.py
```

---

# Dashboard Features

## Executive Overview

Operational KPIs:

- Total shipments
- Customers
- Warehouses
- Average distance
- Delivery time
- Shipment trends
- Priority distribution
- Risk overview

---

## Route Analytics

Provides logistics efficiency analysis:

- Transport performance
- Route distances
- Delivery estimates
- Speed calculations
- Longest routes
- Warehouse route volume

---

## Delivery Risk Analytics

Identifies operational risks:

- Risk categories
- Risk score distribution
- Weather impact
- Temperature analysis
- Wind influence
- Highest-risk shipments

Risk scoring considers:

- Route distance
- Weather conditions

---

## Warehouse Analytics

Provides warehouse intelligence:

- Shipment volume
- Capacity comparison
- Warehouse performance
- Delivery efficiency
- Risk by warehouse
- Geographic locations

---

## Customer Analytics

Explores customer behaviour:

- Shipment frequency
- Customer distribution
- Country activity
- Package preferences
- Top customers

---

# Global Dashboard Filters

All dashboard pages share a common filtering system.

Available filters:

- Warehouse
- Shipment status
- Priority
- Risk category

Filters persist using Streamlit session state.

---

# Project Structure

```text
ShippingDataPipeline/

├── airflow/
│   ├── dags/
│   └── logs/
│
├── dashboard/
│   ├── app.py
│   ├── database.py
│   ├── queries.py
│   │
│   ├── pages/
│   │   ├── Overview.py
│   │   ├── Customers.py
│   │   ├── Routes.py
│   │   ├── Risk.py
│   │   └── Warehouses.py
│   │
│   └── components/
│       ├── sidebar.py
│       ├── filters.py
│       ├── cards.py
│       └── header.py
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── dbt/
│   └── shipping_analytics/
│       ├── models/
│       │   ├── staging/
│       │   └── marts/
│       └── dev.duckdb
│
├── src/
│   ├── extract/
│   ├── transform/
│   ├── warehouse/
│   ├── models/
│   ├── utils/
│   └── pipeline.py
│
├── tests/
│
├── warehouse/
│   └── shipping.duckdb
│
└── README.md
```

---

# Running the Pipeline

From the project root:

```bash
python -m src.pipeline
```

Generates:

- Bronze JSON files
- Silver Parquet files
- Gold analytical datasets
- DuckDB warehouse tables
- Dashboard-ready models

---

# Running dbt

Navigate:

```bash
cd dbt/shipping_analytics
```

Run models:

```bash
dbt run
```

Run tests:

```bash
dbt test
```

---

# Testing

Testing is performed using:

- pytest
- dbt tests

Run Python tests:

```bash
pytest
```

Current validation:

```text
customers              100 rows

dim_customers          100 rows

orders                 300 rows

fact_shipments         300 rows

delivery_performance   300 rows
```

---

# Technical Highlights

- Designed a complete medallion architecture
- Built automated ETL workflows
- Implemented Parquet-based data lake storage
- Created DuckDB analytics warehouse
- Developed dbt dimensional models
- Added data quality testing
- Built interactive Streamlit dashboards
- Implemented global dashboard filtering
- Containerised services with Podman

---

# Design Decisions

## Medallion Architecture

The pipeline separates data into:

```text
Bronze → Silver → Gold
```

Benefits:

- Improved data quality
- Reproducible processing
- Clear data ownership
- Easier debugging

---

## Analytics Engineering Approach

dbt is used to:

- Transform warehouse tables
- Create reusable models
- Document analytics logic
- Validate datasets

---

## Analytical Warehouse Design

DuckDB was selected because it provides:

- Fast analytical queries
- Local warehouse capabilities
- SQL compatibility
- Lightweight deployment

---

# Analytics Capabilities

The platform can answer questions such as:

## Operations

- Which warehouses process the most shipments?
- Which routes are the longest?
- Which transport modes are most efficient?

## Risk Management

- Which shipments have the highest risk?
- How does weather affect delivery?
- Which warehouses have increased operational risk?

## Customer Intelligence

- Which countries generate the most shipments?
- Which customers are most active?
- What package types are most common?

---

# Containerisation

Services can be deployed using Podman.

Architecture:

```text
Fedora Silverblue Host

          |

        Podman

          |

 Analytics Services

          |

 DuckDB Warehouse
```

---

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Data Processing | Polars |
| Storage Format | Parquet |
| Warehouse | DuckDB |
| Transformation | dbt |
| Testing | pytest + dbt tests |
| Orchestration | Airflow |
| Dashboard | Streamlit |
| BI Compatibility | Apache Superset |
| Containers | Podman |
| Operating System | Fedora Silverblue |

---

# Future Improvements

Planned enhancements:

- Airflow DAG scheduling
- Automated dbt execution
- CI/CD pipeline
- Data quality monitoring
- Real-time shipment events
- Predictive delivery delay models
- Machine learning risk prediction
- Cloud deployment
- Dashboard hosting

---

# Project Status

Current implementation:

 Data extraction  
 Bronze/Silver/Gold architecture  
 Parquet data lake  
 DuckDB warehouse  
 dbt staging models  
 dbt analytics marts  
 Automated tests  
 Delivery risk modelling  
 Streamlit dashboard application  
 Global dashboard filtering system  

---

# License

MIT License
