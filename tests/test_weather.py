"""
Tests for WeatherExtractor.
"""

from unittest.mock import patch

import polars as pl
import pytest

from src.extract.weather import WeatherExtractor
from src.config.settings import OPEN_METEO_API

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------


def test_base_url_matches_settings():
    assert WeatherExtractor.BASE_URL == OPEN_METEO_API


# ---------------------------------------------------------------------
# fetch() — mocked HTTP
# ---------------------------------------------------------------------


def test_fetch_makes_one_request_per_warehouse():
    warehouses = pl.DataFrame(
        {
            "warehouse_id": ["WH-001", "WH-002"],
            "latitude": [52.37, 48.86],
            "longitude": [4.90, 2.35],
        }
    )

    payload = {"current_weather": {"temperature": 18.5, "windspeed": 6.2}}

    with patch("src.extract.weather.requests.get") as mock_get:
        mock_get.return_value.json.return_value = payload
        mock_get.return_value.raise_for_status.return_value = None

        records = WeatherExtractor().fetch(warehouses)

    assert len(records) == 2
    assert mock_get.call_count == 2
    assert records[0]["warehouse_id"] == "WH-001"
    assert records[1]["warehouse_id"] == "WH-002"
    assert records[0]["temperature"] == 18.5
    assert records[0]["wind_speed"] == 6.2


# ---------------------------------------------------------------------
# transform()
# ---------------------------------------------------------------------


def test_transform_returns_expected_schema():
    df = WeatherExtractor().transform(
        [
            {
                "warehouse_id": "WH-001",
                "timestamp": "2026-01-01T00:00:00",
                "temperature": 20.5,
                "wind_speed": 10.2,
            },
        ]
    )

    assert isinstance(df, pl.DataFrame)
    assert df.height == 1
    assert {"warehouse_id", "timestamp", "temperature", "wind_speed"} <= set(df.columns)


def test_transform_preserves_row_count():
    records = [
        {
            "warehouse_id": f"WH-{i:03d}",
            "timestamp": "2026-01-01",
            "temperature": 20.0,
            "wind_speed": 5.0,
        }
        for i in range(4)
    ]
    assert WeatherExtractor().transform(records).height == 4


def test_transform_preserves_value_types():
    df = WeatherExtractor().transform(
        [
            {
                "warehouse_id": "WH-001",
                "timestamp": "2026-01-01",
                "temperature": 20.5,
                "wind_speed": 10.2,
            },
        ]
    )

    assert df.schema["temperature"] == pl.Float64
    assert df.schema["wind_speed"] == pl.Float64


# ---------------------------------------------------------------------
# save()
# ---------------------------------------------------------------------


def test_save_writes_parquet_roundtrip(tmp_path):
    df = pl.DataFrame(
        {
            "warehouse_id": ["WH-001"],
            "timestamp": ["2026-01-01T00:00:00"],
            "temperature": [25.0],
            "wind_speed": [5.0],
        }
    )

    saved = WeatherExtractor().save(df, output_dir=tmp_path)

    assert saved.exists()
    assert saved.suffix == ".parquet"

    reloaded = pl.read_parquet(saved)
    assert reloaded.shape == df.shape
    assert reloaded.equals(df)


def test_save_creates_missing_directories(tmp_path):
    nested = tmp_path / "does" / "not" / "exist"
    df = pl.DataFrame(
        {
            "warehouse_id": ["WH-001"],
            "timestamp": ["2026-01-01T00:00:00"],
            "temperature": [25.0],
            "wind_speed": [5.0],
        }
    )

    saved = WeatherExtractor().save(df, output_dir=nested)

    assert nested.is_dir()
    assert saved.exists()
