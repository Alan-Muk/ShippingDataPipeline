# Weather Data Engineering Pipeline

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas)
![Apache Airflow](https://img.shields.io/badge/Airflow-3.x-017CEE?logo=apacheairflow)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![ETL](https://img.shields.io/badge/Pipeline-ETL-success)
![License](https://img.shields.io/badge/License-MIT-green)

A production-style ETL pipeline that ingests, transforms, and stores weather data for analytics workflows.

The system demonstrates a complete data engineering lifecycle:

- External API ingestion
- Raw data storage
- Data transformation
- Relational database loading
- Workflow orchestration using Apache Airflow

---

# Overview

Weather Data Engineering Pipeline is an automated data processing system designed to collect and prepare weather information for analysis.

The pipeline workflow:

```text
Weather API
      |
      ↓
Data Ingestion
      |
      ↓
Raw Data Storage
      |
      ↓
Transformation Layer
      |
      ↓
Analytics Dataset
      |
      ↓
Database Storage
      |
      ↓
Airflow Orchestration
```

The project follows modern ETL principles by separating extraction, transformation, and loading responsibilities into independent processing stages.

---

# Problem

Weather APIs provide raw data that is often unsuitable for analytics without additional processing.

A production-ready data workflow needs to handle:

- External API communication
- Data consistency
- Schema normalization
- Historical storage
- Automated execution

This project explores how raw external data can be transformed into a reliable analytics-ready dataset.

---

# Architecture

## System Architecture

```text
              OpenWeatherMap API

                       |
                       ↓

              Python Ingestion Layer

                       |
                       ↓

              Raw Data Lake Storage

                       |
                       ↓

              Pandas Transformation

                       |
                       ↓

          Structured Database Layer

                       |
                       ↓

              Airflow Workflow Engine
```

---

# Components

## Data Ingestion Layer

Responsible for extracting weather data from external sources.

Responsibilities:

- Request weather information from APIs
- Handle API communication
- Store raw responses
- Preserve original data for reproducibility

Features:

- Environment-based API configuration
- Error handling
- Timestamped raw files

---

## Raw Data Storage Layer

The pipeline follows a lightweight data lake pattern.

Raw API responses are stored before processing.

Benefits:

- Data reproducibility
- Historical records
- Ability to reprocess without new API calls

Example:

```text
data/raw/

Amsterdam_2026-06-24.json
London_2026-06-24.json
NewYork_2026-06-24.json
```

---

## Transformation Layer

Built using Pandas.

Responsibilities:

- Read raw JSON files
- Extract relevant fields
- Normalize schemas
- Create analytics-ready datasets

Extracted fields include:

- City
- Temperature
- Humidity
- Wind speed
- Timestamp

Output:

```text
processed_weather.csv
```

---

## Database Layer

Processed weather data is loaded into a relational database.

Supports:

- SQLite for local development
- PostgreSQL for production-style deployments

Responsibilities:

- Store historical records
- Enable SQL queries
- Provide structured analytics access

---

## Workflow Orchestration

Apache Airflow manages pipeline execution.

Responsibilities:

- Schedule ETL workflows
- Manage task dependencies
- Provide repeatable execution

Pipeline DAG:

```text
Extract

  ↓

Transform

  ↓

Load
```

---

# Core Features

## Multi-City Weather Collection

- Supports multiple locations
- Extensible city configuration
- Automated data retrieval

---

## ETL Pipeline Architecture

Clear separation between:

```text
Extract → Transform → Load
```

Each stage can be developed, tested, and maintained independently.

---

## Data Lake Pattern

Raw data is preserved before transformation.

Advantages:

- Reprocessing capability
- Data auditing
- Pipeline debugging

---

## Database Integration

The pipeline provides:

- Structured storage
- Historical weather records
- SQL querying support

---

# Project Structure

```text
weather-pipeline/

├── ingestion/
│   ├── fetch_weather.py
│   ├── transform_weather.py
│   └── load_to_db.py
│
├── airflow/
│   └── dags/
│       └── weather_pipeline.py
│
├── data/
│   ├── raw/
│   └── processed_weather.csv
│
├── config/
│   └── .env
│
├── weather.db
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Example Data Flow

```text
Amsterdam Weather API

          ↓

data/raw/Amsterdam_2026-06-24.json

          ↓

Pandas Transformation

          ↓

processed_weather.csv

          ↓

weather.db
```

---

# Technical Highlights

- Designed a complete ETL pipeline architecture
- Implemented API-based data ingestion
- Built reusable transformation workflows
- Applied data lake storage principles
- Designed relational database schemas
- Automated workflows using Airflow
- Containerized development environment

---

# Design Decisions

## Raw Data Preservation

Raw API responses are stored before processing.

This allows:

- Re-running transformations
- Debugging incorrect outputs
- Maintaining historical snapshots

---

## Modular Pipeline Stages

Each pipeline stage has a single responsibility:

```text
fetch_weather.py

        ↓

transform_weather.py

        ↓

load_to_db.py
```

This improves:

- Maintainability
- Testing
- Extensibility

---

## Batch Processing Model

The current pipeline processes collected files in batches.

This approach provides:

- Simple execution model
- Reliable processing
- Easy recovery from failures

---

# Setup Instructions

## Clone Repository

```bash
git clone https://github.com/your-username/weather-pipeline.git

cd weather-pipeline
```

---

## Configure Environment Variables

Create:

```text
config/.env
```

Add:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Pipeline

## Extract

```bash
python ingestion/fetch_weather.py
```

---

## Transform

```bash
python ingestion/transform_weather.py
```

---

## Load

```bash
python ingestion/load_to_db.py
```

---

# Running with Airflow

Initialize Airflow:

```bash
airflow db init
```

Start services:

```bash
airflow webserver

airflow scheduler
```

---

# Key Engineering Concepts

This project demonstrates:

- ETL pipeline design
- Data lake architecture
- API integration
- Batch processing
- Data transformation
- Relational database design
- Workflow orchestration
- Modular Python engineering

---

# Challenges

## Data Quality

External APIs may return inconsistent data.

Solution:

- Schema normalization
- Controlled transformations
- Structured outputs

---

## Pipeline Reliability

Automated workflows require predictable execution.

Solution:

- Airflow orchestration
- Modular pipeline stages
- Repeatable processing

---

## Data Reproducibility

Processing should not depend on repeated API calls.

Solution:

- Raw data preservation
- Historical snapshots

---

# Future Improvements

- Add real-time streaming ingestion with Kafka or Redis Streams
- Replace SQLite with PostgreSQL production deployment
- Add data validation using Great Expectations
- Add monitoring with Prometheus and Grafana
- Deploy pipeline to AWS/GCP
- Add CI/CD testing workflows
- Build analytics dashboard using React or Streamlit

---

# License

MIT License
