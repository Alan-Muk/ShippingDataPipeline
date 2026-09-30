"""
Tests for CustomerGenerator and CustomerTransformer.
"""

import polars as pl
import pytest

from src.extract.customers import CustomerGenerator, EU_CITIES
from src.transform.customers import CustomerTransformer

# ---------------------------------------------------------------------
# CustomerGenerator
# ---------------------------------------------------------------------


def test_fetch_returns_requested_count():
    payload = CustomerGenerator().fetch(10)

    assert isinstance(payload, dict)
    assert "results" in payload
    assert len(payload["results"]) == 10


def test_generated_records_have_all_required_fields():
    payload = CustomerGenerator().fetch(5)

    required = {
        "customer_id",
        "title",
        "first_name",
        "last_name",
        "gender",
        "email",
        "phone",
        "street_number",
        "street_name",
        "city",
        "state",
        "country",
        "postcode",
        "latitude",
        "longitude",
        "registered_date",
        "nationality",
    }

    for record in payload["results"]:
        missing = required - set(record.keys())
        assert not missing, f"Missing fields: {missing}"


def test_generated_customers_are_eu_only():
    payload = CustomerGenerator().fetch(50)
    eu_countries = {city[2] for city in EU_CITIES}

    for record in payload["results"]:
        assert record["country"] in eu_countries


def test_generated_coordinates_are_within_europe_bounds():
    payload = CustomerGenerator().fetch(50)

    for record in payload["results"]:
        assert 35 <= record["latitude"] <= 70
        assert -10 <= record["longitude"] <= 30


def test_generated_customer_ids_are_unique():
    payload = CustomerGenerator().fetch(100)
    ids = [c["customer_id"] for c in payload["results"]]

    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------
# CustomerTransformer
# ---------------------------------------------------------------------


def test_transform_returns_dataframe_with_expected_schema():
    raw = CustomerGenerator().fetch(5)
    df = CustomerTransformer().transform(raw)

    assert isinstance(df, pl.DataFrame)
    assert df.height == 5
    assert {
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "city",
        "state",
        "country",
        "latitude",
        "longitude",
    } <= set(df.columns)


def test_transform_preserves_row_count():
    raw = CustomerGenerator().fetch(20)
    df = CustomerTransformer().transform(raw)

    assert df.height == 20


def test_transform_produces_float_coordinates():
    raw = CustomerGenerator().fetch(5)
    df = CustomerTransformer().transform(raw)

    assert df.schema["latitude"] == pl.Float64
    assert df.schema["longitude"] == pl.Float64
