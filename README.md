# Weather Data Engineering Pipeline

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas)
![Apache Airflow](https://img.shields.io/badge/Airflow-3.x-017CEE?logo=apacheairflow)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![ETL](https://img.shields.io/badge/Pipeline-ETL-success)
![License](https://img.shields.io/badge/License-MIT-green)

A production-style data engineering pipeline that ingests, processes, and stores weather data for analytics use cases.

The system demonstrates a complete **ETL workflow**, including API ingestion, raw data storage, transformation using Pandas, database loading, and orchestration using Apache Airflow.

---

# Architecture

```text id="arch_final"
OpenWeatherMap API
        ↓
Data Ingestion (Python)
        ↓
Raw Data Storage (JSON files - Data Lake Layer)
        ↓
Data Transformation (Pandas ETL)
        ↓
Processed Dataset (CSV / Structured Data)
        ↓
Database Layer (SQLite / PostgreSQL)
        ↓
Orchestration Layer (Apache Airflow)
```

---

# Tech Stack

* **Python** – Core ETL logic and API integration
* **Pandas** – Data transformation and cleaning
* **Requests** – API communication
* **SQLite / PostgreSQL** – Data storage
* **Apache Airflow** – Workflow orchestration
* **Docker / Podman** – Containerized environment
* **JSON / CSV** – Data formats for raw and processed layers

---

# Project Structure

```bash id="structure_final"
weather-pipeline/
│
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
│   ├── *.json
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

# Pipeline Overview

## 1. Data Ingestion (Extract)

* Fetches real-time weather data from **OpenWeatherMap API**
* Supports multiple cities (e.g., Amsterdam, London, New York)
* Stores raw API responses as timestamped JSON files

Key Features:

* Environment variable-based API key management
* Error handling for failed requests
* Local raw data storage (data lake pattern)

---

## 2. Data Transformation (Transform)

* Reads raw JSON files from storage
* Extracts key weather attributes:

  * city
  * temperature
  * humidity
  * wind speed
  * timestamp
* Converts structured data into a Pandas DataFrame
* Outputs cleaned CSV dataset

Key Features:

* Batch file processing using `glob`
* Schema normalization
* Structured analytics-ready dataset

---

## 3. Data Loading (Load)

* Loads transformed dataset into SQLite database
* Creates structured relational table
* Stores historical weather records

Key Features:

* Relational schema design
* Persistent storage layer
* SQL-based querying capability

---

## 4. Workflow Orchestration (Airflow)

* Automates ETL pipeline execution
* Schedules ingestion → transformation → loading steps
* Ensures reproducible and repeatable workflows

---

# Features

## Multi-City Weather Ingestion

* Supports multiple cities
* Extensible city configuration

## Data Lake Design

* Raw JSON files stored for reproducibility
* Enables reprocessing without re-fetching API data

## ETL Pipeline Architecture

* Clear separation of Extract, Transform, Load stages
* Modular Python scripts for each stage

## Database Integration

* SQLite for local development
* Easily extendable to PostgreSQL

## Orchestrated Workflows

* Airflow DAG-based scheduling
* Automated pipeline execution

---

# Example Data Flow

```text id="flow_final"
Amsterdam API Response
        ↓
data/raw/Amsterdam_2026-06-24.json
        ↓
Pandas Transformation
        ↓
processed_weather.csv
        ↓
weather.db (SQLite table)
```

---

# Setup Instructions

## 1. Clone Repository

```bash id="setup1"
git clone https://github.com/your-username/weather-pipeline.git
cd weather-pipeline
```

---

## 2. Configure Environment Variables

Create a `.env` file inside `config/`:

```env id="env1"
OPENWEATHER_API_KEY=your_api_key_here
```

Get API key here:
[OpenWeatherMap API](https://openweathermap.org/api?utm_source=chatgpt.com)

---

## 3. Install Dependencies

```bash id="setup2"
pip install -r requirements.txt
```

---

## 4. Run Pipeline Manually

### Step 1: Ingest Data

```bash id="run1"
python ingestion/fetch_weather.py
```

### Step 2: Transform Data

```bash id="run2"
python ingestion/transform_weather.py
```

### Step 3: Load into Database

```bash id="run3"
python ingestion/load_to_db.py
```

---

## 5. Run with Airflow (Optional)

```bash id="airflow1"
airflow db init
airflow webserver
airflow scheduler
```

---

# Key Engineering Concepts Demonstrated

* ETL (Extract, Transform, Load) pipeline design
* Data lake architecture (raw JSON storage)
* Batch processing workflows
* API integration and external data ingestion
* Relational database design
* Workflow orchestration using Airflow
* Modular and reusable Python architecture
* Reproducible data pipelines

---

# Future Improvements

* Add real-time streaming ingestion (Kafka / Redis Streams)
* Replace SQLite with PostgreSQL or cloud warehouse
* Add data validation layer (Great Expectations)
* Implement logging + monitoring (Prometheus / Grafana)
* Deploy pipeline to cloud (AWS / GCP)
* Add CI/CD for automated pipeline testing
* Build dashboard (React / Streamlit) for visualization

---

# License

MIT License
