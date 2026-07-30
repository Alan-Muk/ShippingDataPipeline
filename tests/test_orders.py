import polars as pl

from src.extract.orders import OrderGenerator


def create_test_customers():
    """
    Create a small fake customer dataframe.
    """

    return pl.DataFrame(
        {
            "customer_id": [
                "cust-001",
                "cust-002",
            ],
            "first_name": [
                "John",
                "Jane",
            ],
        }
    )


def test_order_generation_creates_correct_amount():

    customers = create_test_customers()

    generator = OrderGenerator()

    warehouses = create_test_warehouses()

    orders = generator.generate(
        customers,
        warehouses,
        orders_per_customer=3,
    )

    assert isinstance(orders, pl.DataFrame)

    # 2 customers * 3 orders each
    assert orders.height == 6


def test_orders_have_required_columns():

    customers = create_test_customers()

    generator = OrderGenerator()

    warehouses = create_test_warehouses()

    orders = generator.generate(
        customers,
        warehouses,
        orders_per_customer=3,
    )

    expected_columns = {
        "order_id",
        "customer_id",
        "package_weight_kg",
        "package_size",
        "priority",
        "status",
        "created_at",
    }

    assert expected_columns.issubset(
        set(orders.columns)
    )


def test_orders_reference_existing_customers():

    customers = create_test_customers()

    generator = OrderGenerator()

    warehouses = create_test_warehouses()

    orders = generator.generate(
        customers,
        warehouses,
        orders_per_customer=3,
    )

    order_customer_ids = set(
        orders["customer_id"]
    )

    customer_ids = set(
        customers["customer_id"]
    )

    assert order_customer_ids.issubset(
        customer_ids
    )


def test_order_values_are_valid():

    customers = create_test_customers()

    generator = OrderGenerator()

    warehouses = create_test_warehouses()

    orders = generator.generate(
        customers,
        warehouses,
        orders_per_customer=3,
    )

    assert orders["package_weight_kg"].min() > 0

    assert orders["priority"].is_in(
        [
            "standard",
            "express",
            "priority",
        ]
    ).all()

    assert orders["status"].is_in(
        [
            "created",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
        ]
    ).all()

def create_test_warehouses():

    return pl.DataFrame(
        {
            "warehouse_id": [
                "WH-001",
                "WH-002",
            ]
        }
    )

def test_orders_reference_existing_warehouses():

    customers = create_test_customers()
    warehouses = create_test_warehouses()

    generator = OrderGenerator()

    orders = generator.generate(
        customers,
        warehouses,
        orders_per_customer=5,
    )

    order_warehouse_ids = set(
        orders["warehouse_id"]
    )

    warehouse_ids = set(
        warehouses["warehouse_id"]
    )

    assert order_warehouse_ids.issubset(
        warehouse_ids
    )

def test_orders_have_warehouse_id():

    customers = create_test_customers()
    warehouses = create_test_warehouses()

    generator = OrderGenerator()

    orders = generator.generate(
        customers,
        warehouses,
        orders_per_customer=2,
    )

    assert "warehouse_id" in orders.columns