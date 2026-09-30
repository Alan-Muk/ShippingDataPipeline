"""
Tests for OrderGenerator.
"""

import polars as pl

from src.extract.orders import OrderGenerator

# ---------------------------------------------------------------------
# Row count
# ---------------------------------------------------------------------


def test_generation_returns_dataframe(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(
        sample_customers,
        sample_warehouses,
        orders_per_customer=3,
    )

    assert isinstance(orders, pl.DataFrame)
    assert orders.height == sample_customers.height * 3


def test_orders_per_customer_is_respected(sample_customers, sample_warehouses):
    for n in (1, 4, 10):
        orders = OrderGenerator().generate(
            sample_customers,
            sample_warehouses,
            orders_per_customer=n,
        )
        assert orders.height == sample_customers.height * n


# ---------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------


def test_orders_have_required_columns(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 3)

    assert {
        "order_id",
        "customer_id",
        "warehouse_id",
        "package_weight_kg",
        "package_size",
        "priority",
        "status",
        "created_at",
    } <= set(orders.columns)


def test_order_ids_are_unique(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 5)

    assert orders["order_id"].n_unique() == orders.height


# ---------------------------------------------------------------------
# Referential integrity
# ---------------------------------------------------------------------


def test_orders_reference_existing_customers(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 3)

    assert set(orders["customer_id"]) <= set(sample_customers["customer_id"])


def test_orders_reference_existing_warehouses(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 5)

    assert set(orders["warehouse_id"]) <= set(sample_warehouses["warehouse_id"])


# ---------------------------------------------------------------------
# Value validation
# ---------------------------------------------------------------------


def test_package_weights_are_positive_and_bounded(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 5)

    assert (orders["package_weight_kg"] > 0).all()
    assert (orders["package_weight_kg"] <= 30).all()


def test_priorities_are_from_known_set(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 5)

    assert orders["priority"].is_in(["standard", "express", "priority"]).all()


def test_statuses_are_from_known_set(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 5)

    assert (
        orders["status"]
        .is_in(["created", "processing", "shipped", "delivered", "cancelled"])
        .all()
    )


def test_package_sizes_are_from_known_set(sample_customers, sample_warehouses):
    orders = OrderGenerator().generate(sample_customers, sample_warehouses, 5)

    assert orders["package_size"].is_in(["small", "medium", "large"]).all()
