"""
Shared pytest fixtures for the ShippingDataPipeline test suite.

Fixtures here provide:
  * Small in-memory Polars DataFrames for generator tests
  * A temp-directory sandbox so tests never touch the real data/
  * A fresh WarehouseLoader pointed at a throwaway DuckDB file
"""

from pathlib import Path

import polars as pl
import pytest

# ---------------------------------------------------------------------
# In-memory data fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def sample_customers() -> pl.DataFrame:
    """Minimal customer DataFrame for generator tests."""
    return pl.DataFrame(
        {
            "customer_id": ["cust-001", "cust-002"],
            "first_name": ["John", "Jane"],
            "last_name": ["Smith", "Doe"],
            "latitude": [52.37, 48.86],
            "longitude": [4.90, 2.35],
        }
    )


@pytest.fixture
def sample_warehouses() -> pl.DataFrame:
    """Minimal warehouse DataFrame for generator tests."""
    return pl.DataFrame(
        {
            "warehouse_id": ["WH-001", "WH-002"],
            "latitude": [52.52, 48.85],
            "longitude": [13.41, 2.35],
        }
    )


@pytest.fixture
def sample_orders() -> pl.DataFrame:
    """Minimal orders DataFrame for route tests."""
    return pl.DataFrame(
        {
            "order_id": ["ORD-001", "ORD-002"],
            "customer_id": ["cust-001", "cust-002"],
            "warehouse_id": ["WH-001", "WH-002"],
        }
    )


@pytest.fixture
def sample_weather() -> pl.DataFrame:
    """Minimal weather DataFrame for risk tests."""
    return pl.DataFrame(
        {
            "warehouse_id": ["WH-001", "WH-002"],
            "timestamp": ["2026-01-01T00:00:00", "2026-01-01T00:00:00"],
            "temperature": [20.0, 25.0],
            "wind_speed": [5.0, 12.0],
        }
    )


# ---------------------------------------------------------------------
# Sandboxed settings — point data directories at a temp folder
# ---------------------------------------------------------------------


@pytest.fixture
def sandbox_data_dirs(tmp_path, monkeypatch):
    """
    Redirect BRONZE_DIR / SILVER_DIR / GOLD_DIR to a temp tree for the
    duration of a test. Prevents tests from writing to the real data/.
    """
    bronze = tmp_path / "bronze"
    silver = tmp_path / "silver"
    gold = tmp_path / "gold"

    for name, value in (
        ("BRONZE_DIR", bronze),
        ("SILVER_DIR", silver),
        ("GOLD_DIR", gold),
    ):
        monkeypatch.setattr(f"src.config.settings.{name}", value)
        # Some modules import the constant directly — patch those too
        for mod in (
            "src.extract.customers",
            "src.extract.weather",
            "src.extract.warehouses",
            "src.extract.orders",
            "src.transform.customers",
            "src.transform.routes",
            "src.transform.delivery_risk",
        ):
            monkeypatch.setattr(f"{mod}.{name}", value, raising=False)

    yield {"bronze": bronze, "silver": silver, "gold": gold}


# ---------------------------------------------------------------------
# Sandboxed DuckDB
# ---------------------------------------------------------------------


@pytest.fixture
def sandbox_duckdb(tmp_path, monkeypatch):
    """Redirect DUCKDB_PATH to a temp file for the duration of a test."""
    db = tmp_path / "test.duckdb"
    monkeypatch.setattr("src.config.settings.DUCKDB_PATH", db)
    monkeypatch.setattr("src.warehouse.load.DUCKDB_PATH", db, raising=False)
    return db


@pytest.fixture
def warehouses() -> pl.DataFrame:
    """A freshly generated warehouse DataFrame."""
    from src.extract.warehouses import WarehouseGenerator

    return WarehouseGenerator().generate()
