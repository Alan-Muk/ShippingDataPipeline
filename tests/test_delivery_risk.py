import polars as pl

from src.transform.delivery_risk import (
    DeliveryRiskTransformer,
)


def test_high_risk_route():

    transformer = DeliveryRiskTransformer()

    score = transformer.calculate_risk_score(
        distance_km=800,
        wind_speed=40,
    )

    assert score >= 60


def test_risk_classification():

    transformer = DeliveryRiskTransformer()

    assert (
        transformer.risk_level(10)
        == "LOW"
    )

    assert (
        transformer.risk_level(40)
        == "MEDIUM"
    )

    assert (
        transformer.risk_level(80)
        == "HIGH"
    )


def test_delivery_risk_transform():

    transformer = DeliveryRiskTransformer()

    routes = pl.DataFrame(
        {
            "route_id": ["RT-001"],
            "order_id": ["ORD-001"],
            "warehouse_id": ["WH-001"],
            "distance_km": [600],
            "estimated_hours": [10],
        }
    )

    weather = pl.DataFrame(
        {
            "warehouse_id": ["WH-001"],
            "temperature": [18],
            "wind_speed": [35],
        }
    )

    result = transformer.transform(
        routes,
        weather,
    )

    assert result.height == 1
    assert result["risk_level"][0] == "HIGH"