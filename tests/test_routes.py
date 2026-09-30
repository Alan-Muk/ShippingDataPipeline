"""
Tests for RouteTransformer.

The transformer is vectorised — haversine is expressed as a Polars
expression, not a scalar method. We test via `transform()` and
verify distance, mode, duration, and ID derivation behaviour.
"""

import math

import polars as pl
import pytest

from src.transform.routes import (
    EARTH_RADIUS_KM,
    HANDLING_HOURS,
    MODE_DISTANCE_TIERS,
    TRANSPORT_SPEEDS_KMH,
    RouteTransformer,
)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _make_routes(
    transformer: RouteTransformer,
    *,
    order_id: str = "ORD-001",
    customer_lat: float = 52.3676,
    customer_lon: float = 4.9041,
    warehouse_lat: float = 52.5200,
    warehouse_lon: float = 13.4050,
) -> pl.DataFrame:
    """Build a single-row routes DataFrame for the given coordinates."""
    return transformer.transform(
        orders=pl.DataFrame(
            {
                "order_id": [order_id],
                "customer_id": ["CUST-001"],
                "warehouse_id": ["WH-001"],
            }
        ),
        customers=pl.DataFrame(
            {
                "customer_id": ["CUST-001"],
                "latitude": [customer_lat],
                "longitude": [customer_lon],
            }
        ),
        warehouses=pl.DataFrame(
            {
                "warehouse_id": ["WH-001"],
                "latitude": [warehouse_lat],
                "longitude": [warehouse_lon],
            }
        ),
    )


def _make_routes_at_distance(
    transformer: RouteTransformer,
    distance_km: float,
) -> pl.DataFrame:
    """
    Build a route with approximately `distance_km` separation by moving
    the customer eastward from a fixed warehouse at (50°N, 5°E).
    """
    # At 50°N, 1 degree of longitude ≈ 111.32 * cos(50°) ≈ 71.6 km
    deg_per_km = 1 / (111.32 * math.cos(math.radians(50.0)))
    lon_offset = distance_km * deg_per_km

    return _make_routes(
        transformer,
        customer_lat=50.0,
        customer_lon=5.0 + lon_offset,
        warehouse_lat=50.0,
        warehouse_lon=5.0,
    )


@pytest.fixture
def transformer():
    return RouteTransformer()


# ---------------------------------------------------------------------
# Row identity pass-through
# ---------------------------------------------------------------------


def test_route_preserves_identifiers(transformer):
    routes = _make_routes(transformer)

    assert routes.height == 1
    assert routes["order_id"][0] == "ORD-001"
    assert routes["customer_id"][0] == "CUST-001"
    assert routes["warehouse_id"][0] == "WH-001"


def test_route_has_expected_columns(transformer):
    routes = _make_routes(transformer)

    assert {
        "route_id",
        "order_id",
        "customer_id",
        "warehouse_id",
        "distance_km",
        "estimated_hours",
        "transport_mode",
    } <= set(routes.columns)


# ---------------------------------------------------------------------
# Distance (haversine)
# ---------------------------------------------------------------------


def test_distance_amsterdam_to_berlin(transformer):
    """
    Reference distance from an independent haversine computation:
    Amsterdam (52.3676, 4.9041) → Berlin (52.5200, 13.4050) is ~577 km.
    """
    routes = _make_routes(transformer)

    distance = routes["distance_km"][0]
    assert 565 <= distance <= 590


def test_distance_zero_for_identical_coordinates(transformer):
    same = dict(
        customer_lat=52.0, customer_lon=4.0, warehouse_lat=52.0, warehouse_lon=4.0
    )
    routes = _make_routes(transformer, **same)

    assert routes["distance_km"][0] == pytest.approx(0.0, abs=1e-6)


def test_distance_never_negative(transformer):
    routes = transformer.transform(
        orders=pl.DataFrame(
            {
                "order_id": [f"ORD-{i:03d}" for i in range(5)],
                "customer_id": [f"CUST-{i:03d}" for i in range(5)],
                "warehouse_id": ["WH-001"] * 5,
            }
        ),
        customers=pl.DataFrame(
            {
                "customer_id": [f"CUST-{i:03d}" for i in range(5)],
                "latitude": [35.0, 45.0, 55.0, 65.0, 40.0],
                "longitude": [-9.0, 0.0, 10.0, 20.0, -5.0],
            }
        ),
        warehouses=pl.DataFrame(
            {
                "warehouse_id": ["WH-001"],
                "latitude": [50.0],
                "longitude": [5.0],
            }
        ),
    )

    assert (routes["distance_km"] >= 0).all()


# ---------------------------------------------------------------------
# Transport mode assignment
# ---------------------------------------------------------------------


def test_short_distance_is_van(transformer):
    routes = _make_routes_at_distance(transformer, 300)
    assert routes["transport_mode"][0] == "van"


def test_mid_distance_is_truck(transformer):
    routes = _make_routes_at_distance(transformer, 1_500)
    assert routes["transport_mode"][0] == "truck"


def test_long_distance_is_air(transformer):
    routes = _make_routes_at_distance(transformer, 8_000)
    assert routes["transport_mode"][0] == "air"


# ---------------------------------------------------------------------
# Estimated hours
# ---------------------------------------------------------------------


def test_hours_match_mode_formula(transformer):
    routes = _make_routes_at_distance(transformer, 1_500)
    mode = routes["transport_mode"][0]
    expected = (
        routes["distance_km"][0] / TRANSPORT_SPEEDS_KMH[mode] + HANDLING_HOURS[mode]
    )

    assert routes["estimated_hours"][0] == pytest.approx(expected, abs=0.02)


def test_hours_are_positive(transformer):
    routes = _make_routes(transformer)
    assert routes["estimated_hours"][0] > 0


# ---------------------------------------------------------------------
# route_id derivation
# ---------------------------------------------------------------------


def test_route_id_is_deterministic(transformer):
    a = _make_routes(transformer, order_id="ORD-XYZ-1234567890")
    b = _make_routes(transformer, order_id="ORD-XYZ-1234567890")

    assert a["route_id"][0] == b["route_id"][0]


def test_route_id_prefixed_and_derived_from_order_id(transformer):
    routes = _make_routes(transformer, order_id="abcdefgh1234-xyz")

    assert routes["route_id"][0] == "RT-abcdefgh1234-xyz"


def test_route_ids_are_unique_across_orders(transformer):
    orders = pl.DataFrame(
        {
            "order_id": [f"ORD-{i:012d}" for i in range(20)],
            "customer_id": ["CUST-001"] * 20,
            "warehouse_id": ["WH-001"] * 20,
        }
    )
    routes = transformer.transform(
        orders=orders,
        customers=pl.DataFrame(
            {
                "customer_id": ["CUST-001"],
                "latitude": [52.0],
                "longitude": [4.0],
            }
        ),
        warehouses=pl.DataFrame(
            {
                "warehouse_id": ["WH-001"],
                "latitude": [50.0],
                "longitude": [5.0],
            }
        ),
    )

    assert routes["route_id"].n_unique() == 20


# ---------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------


def test_speeds_reflect_typical_logistics():
    """Air >> van > truck is the realistic ordering."""
    speeds = TRANSPORT_SPEEDS_KMH
    assert speeds["air"] > speeds["van"]
    assert speeds["van"] > speeds["truck"]


def test_handling_hours_are_non_negative():
    assert all(h >= 0 for h in HANDLING_HOURS.values())


def test_mode_tiers_are_sorted_low_to_high():
    bounds = [b for b, _ in MODE_DISTANCE_TIERS]
    assert bounds == sorted(bounds)


def test_earth_radius_is_realistic():
    assert 6_300 <= EARTH_RADIUS_KM <= 6_400
