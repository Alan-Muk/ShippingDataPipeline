import polars as pl

from src.transform.routes import RouteTransformer


def test_haversine():
    transformer = RouteTransformer()

    distance = transformer.haversine(
        52.3676,
        4.9041,
        52.5200,
        13.4050,
    )

    assert distance > 500
    assert distance < 600


def test_route_generation():
    transformer = RouteTransformer()

    orders = pl.DataFrame(
        {
            "order_id": ["ORD-001"],
            "customer_id": ["CUST-001"],
            "warehouse_id": ["WH-001"],
        }
    )

    customers = pl.DataFrame(
        {
            "customer_id": ["CUST-001"],
            "latitude": [52.52],
            "longitude": [13.40],
        }
    )

    warehouses = pl.DataFrame(
        {
            "warehouse_id": ["WH-001"],
            "latitude": [52.36],
            "longitude": [4.90],
        }
    )

    routes = transformer.transform(
        orders,
        customers,
        warehouses,
    )

    assert routes.height == 1
    assert "distance_km" in routes.columns
    assert routes["distance_km"][0] > 0
