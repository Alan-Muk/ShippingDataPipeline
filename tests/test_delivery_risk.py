"""
Tests for the vectorised DeliveryRiskTransformer.

Because the transformer is now expression-based, we test behaviour
through the public `transform()` entry point rather than by calling
removed helpers like `calculate_risk_score` / `risk_level`.
"""

import polars as pl
import pytest

from src.transform.delivery_risk import (
    DISTANCE_TIERS_KM,
    DURATION_TIERS_H,
    RISK_LEVELS,
    TEMPERATURE_TIERS_C,
    UNKNOWN_WEATHER_PENALTY,
    WIND_TIERS_KMH,
    DeliveryRiskTransformer,
)

VALID_LEVELS = {label for _, label in RISK_LEVELS}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _routes(**overrides) -> pl.DataFrame:
    """One-row routes DataFrame with sane defaults."""
    row = {
        "route_id": ["RT-0001"],
        "order_id": ["ORD-0001"],
        "warehouse_id": ["WH-001"],
        "distance_km": [100.0],
        "estimated_hours": [3.0],
        "transport_mode": ["van"],
    }
    row.update({k: [v] for k, v in overrides.items()})
    return pl.DataFrame(row)


def _weather(**overrides) -> pl.DataFrame:
    row = {
        "warehouse_id": ["WH-001"],
        "temperature": [20.0],
        "wind_speed": [5.0],
        "timestamp": ["2026-01-01T00:00:00"],
    }
    row.update({k: [v] for k, v in overrides.items()})
    return pl.DataFrame(row)


def _tier_points(tiers: list[tuple[float, int]], value: float) -> int:
    """Mirror of the transformer's tier resolution: highest match wins."""
    points = 0
    for bound, pts in tiers:
        if value > bound:
            points = pts
    return points


# ---------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------


def test_transform_returns_one_row_per_route():
    routes = _routes()
    result = DeliveryRiskTransformer().transform(routes, _weather())

    assert result.height == routes.height


def test_transform_returns_expected_columns():
    result = DeliveryRiskTransformer().transform(_routes(), _weather())

    assert {
        "route_id",
        "order_id",
        "warehouse_id",
        "distance_km",
        "estimated_hours",
        "temperature",
        "wind_speed",
        "risk_score",
        "risk_level",
    } <= set(result.columns)


# ---------------------------------------------------------------------
# Score composition
# ---------------------------------------------------------------------


def test_score_matches_tier_composition():
    """Score should equal the sum of tier points for the input values."""
    distance, hours, temp, wind = 12_000.0, 40.0, 28.0, 18.0

    result = DeliveryRiskTransformer().transform(
        _routes(distance_km=distance, estimated_hours=hours),
        _weather(temperature=temp, wind_speed=wind),
    )

    expected = min(
        _tier_points(DISTANCE_TIERS_KM, distance)
        + _tier_points(DURATION_TIERS_H, hours)
        + _tier_points(TEMPERATURE_TIERS_C, temp)
        + _tier_points(WIND_TIERS_KMH, wind),
        100,
    )
    assert result["risk_score"][0] == expected


def test_score_never_exceeds_100():
    result = DeliveryRiskTransformer().transform(
        _routes(distance_km=25_000.0, estimated_hours=200.0),
        _weather(temperature=45.0, wind_speed=80.0),
    )

    assert result["risk_score"][0] <= 100


def test_score_is_non_negative():
    result = DeliveryRiskTransformer().transform(_routes(), _weather())

    assert result["risk_score"][0] >= 0


# ---------------------------------------------------------------------
# Risk levels
# ---------------------------------------------------------------------


def test_risk_level_is_always_a_valid_category():
    result = DeliveryRiskTransformer().transform(_routes(), _weather())

    assert result["risk_level"][0] in VALID_LEVELS


def test_benign_route_is_low_risk():
    result = DeliveryRiskTransformer().transform(
        _routes(distance_km=300.0, estimated_hours=5.0),
        _weather(temperature=18.0, wind_speed=3.0),
    )

    assert result["risk_level"][0] == "LOW"


def test_high_risk_long_haul_bad_weather():
    result = DeliveryRiskTransformer().transform(
        _routes(distance_km=12_000.0, estimated_hours=40.0),
        _weather(temperature=28.0, wind_speed=18.0),
    )

    assert result["risk_level"][0] in {"HIGH", "CRITICAL"}
    assert result["risk_score"][0] >= 50


# ---------------------------------------------------------------------
# Missing weather
# ---------------------------------------------------------------------


def test_missing_weather_is_handled_gracefully():
    routes = _routes(distance_km=1_000.0)
    weather = _weather(warehouse_id="WH-999")

    result = DeliveryRiskTransformer().transform(routes, weather)

    assert result.height == 1
    assert result["risk_score"][0] >= 0


# ---------------------------------------------------------------------
# Batch behaviour
# ---------------------------------------------------------------------


def test_batch_returns_row_per_route():
    routes = pl.DataFrame(
        {
            "route_id": [f"RT-{i:04d}" for i in range(5)],
            "order_id": [f"ORD-{i:04d}" for i in range(5)],
            "warehouse_id": ["WH-001"] * 5,
            "distance_km": [100.0, 1_000.0, 5_000.0, 10_000.0, 20_000.0],
            "estimated_hours": [2.0, 8.0, 24.0, 48.0, 120.0],
            "transport_mode": ["van", "van", "truck", "truck", "air"],
        }
    )
    weather = _weather(temperature=22.0, wind_speed=8.0)

    result = DeliveryRiskTransformer().transform(routes, weather)

    assert result.height == 5
    assert all(level in VALID_LEVELS for level in result["risk_level"].to_list())


# ---------------------------------------------------------------------
# Tuning constants
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "tiers",
    [
        DISTANCE_TIERS_KM,
        DURATION_TIERS_H,
        TEMPERATURE_TIERS_C,
        WIND_TIERS_KMH,
    ],
)
def test_tier_lists_are_sorted_low_to_high(tiers):
    bounds = [b for b, _ in tiers]
    assert bounds == sorted(bounds)


def test_unknown_weather_penalty_is_reasonable():
    assert 0 < UNKNOWN_WEATHER_PENALTY <= 25
