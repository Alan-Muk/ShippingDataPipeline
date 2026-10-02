"""
Airflow DAG: Shipping Data Pipeline

Runs the end-to-end Python ETL pipeline:
    customers -> warehouses -> weather -> orders -> routes -> risk -> DuckDB

The pipeline itself is a single Python callable (src.pipeline.run_pipeline),
so the DAG is intentionally simple. Future extensions could split the
pipeline into per-step tasks for finer-grained retries.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# The pipeline must be importable from the Airflow worker.
# When running via Docker Compose, we mount the project root into
# /opt/airflow/project and add it to PYTHONPATH (see docker-compose.yml).
from src.pipeline import run_pipeline

default_args = {
    "owner": "shipping-analytics",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}


def _run_pipeline(**context) -> dict:
    """
    Thin wrapper around run_pipeline().

    Returns a summary dict suitable for XCom, so downstream tasks (or
    the Airflow UI) can inspect what happened.
    """
    run = run_pipeline()

    summary = {
        "total_duration_s": round(run.total_duration_s, 2),
        "steps": [
            {
                "name": s.name,
                "duration_s": round(s.duration_s, 2),
                "rows": s.rows,
            }
            for s in run.steps
        ],
    }

    print(f"Pipeline complete: {summary['total_duration_s']}s")
    for step in summary["steps"]:
        print(f"  {step['name']:<22} {step['duration_s']:>6.2f}s  {step['rows'] or ''}")

    return summary


with DAG(
    dag_id="shipping_pipeline",
    description="End-to-end shipping data pipeline (medallion -> DuckDB)",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",  # daily at 06:00 UTC
    catchup=False,
    max_active_runs=1,  # DuckDB is single-writer; no parallel runs
    tags=["shipping", "etl", "duckdb"],
) as dag:

    run_pipeline_task = PythonOperator(
        task_id="run_pipeline",
        python_callable=_run_pipeline,
    )

    run_pipeline_task
