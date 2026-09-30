"""
Tests for the flat Customer Pydantic model.
"""

import pytest
from pydantic import ValidationError

from src.models.customer import Customer

VALID_RECORD = {
    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Mr",
    "first_name": "John",
    "last_name": "Smith",
    "gender": "male",
    "email": "john.smith@example.eu",
    "phone": "+31-20-123-4567",
    "street_number": 42,
    "street_name": "Main Street",
    "city": "Amsterdam",
    "state": "North Holland",
    "country": "Netherlands",
    "postcode": "1012AB",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "registered_date": "2020-01-01T00:00:00",
    "nationality": "NE",
}


def test_model_accepts_valid_record():
    customer = Customer(**VALID_RECORD)

    assert customer.customer_id == "123e4567-e89b-12d3-a456-426614174000"
    assert customer.email == "john.smith@example.eu"
    assert customer.city == "Amsterdam"
    assert customer.country == "Netherlands"


def test_model_preserves_coordinates_as_floats():
    customer = Customer(**VALID_RECORD)

    assert isinstance(customer.latitude, float)
    assert isinstance(customer.longitude, float)
    assert customer.latitude == pytest.approx(52.3676)
    assert customer.longitude == pytest.approx(4.9041)


def test_model_ignores_extra_fields():
    record = {**VALID_RECORD, "unexpected_field": "ignored"}
    customer = Customer(**record)

    assert customer.first_name == "John"
    assert not hasattr(customer, "unexpected_field")


@pytest.mark.parametrize(
    "missing_field",
    [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "latitude",
        "longitude",
        "country",
    ],
)
def test_model_rejects_missing_required_fields(missing_field):
    record = {k: v for k, v in VALID_RECORD.items() if k != missing_field}
    with pytest.raises(ValidationError):
        Customer(**record)


def test_model_coerces_numeric_strings():
    """Pydantic should coerce string numbers into floats."""
    record = {
        **VALID_RECORD,
        "latitude": "52.3676",
        "longitude": "4.9041",
    }
    customer = Customer(**record)

    assert isinstance(customer.latitude, float)
    assert isinstance(customer.longitude, float)
