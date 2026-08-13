import polars as pl

from src.transform.routes import RouteTransformer


def test_route_customer_order_relationship():
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
            "latitude": [52.3676],
            "longitude": [4.9041],
        }
    )

    warehouses = pl.DataFrame(
        {
            "warehouse_id": ["WH-001"],
            "latitude": [52.5200],
            "longitude": [13.4050],
        }
    )

    transformer = RouteTransformer()

    routes = transformer.transform(
        orders,
        customers,
        warehouses,
    )

    assert routes["order_id"][0] == "ORD-001"
    assert routes["customer_id"][0] == "CUST-001"
    assert routes["warehouse_id"][0] == "WH-001"
