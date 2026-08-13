from datetime import datetime, timedelta
from pathlib import Path
import random
import uuid

import polars as pl

from src.config.settings import SILVER_DIR
from src.utils.logger import logger


class OrderGenerator:
    """
    Generate synthetic shipping orders.
    """

    STATUSES = [
        "created",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
    ]

    PRIORITIES = [
        "standard",
        "express",
        "priority",
    ]

    PACKAGE_SIZES = [
        "small",
        "medium",
        "large",
    ]

    def generate(
        self,
        customers_df: pl.DataFrame,
        warehouses_df: pl.DataFrame,
        orders_per_customer: int = 3,
    ) -> pl.DataFrame:
        """
        Generate orders for customers.
        """

        orders = []

        warehouse_list = warehouses_df.to_dicts()
        for customer in customers_df.iter_rows(named=True):
            warehouse = random.choice(warehouse_list)

            for _ in range(orders_per_customer):
                created_date = datetime.now() - timedelta(days=random.randint(0, 90))

                warehouse = random.choice(warehouse_list)

                orders.append(
                    {
                        "order_id": str(uuid.uuid4()),
                        "customer_id": customer["customer_id"],
                        "warehouse_id": warehouse["warehouse_id"],
                        "package_weight_kg": round(
                            random.uniform(0.5, 25),
                            2,
                        ),
                        "package_size": random.choice(self.PACKAGE_SIZES),
                        "priority": random.choice(self.PRIORITIES),
                        "status": random.choice(self.STATUSES),
                        "created_at": created_date,
                    }
                )

        df = pl.DataFrame(orders)

        logger.info(f"Generated {df.height} orders")

        return df

    def save(self, df: pl.DataFrame) -> Path:
        """
        Save orders to Silver layer.
        """

        output_dir = SILVER_DIR / "orders"

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_dir / "orders.parquet"

        df.write_parquet(output_file)

        logger.info(f"Saved orders parquet: {output_file}")

        return output_file


"""
OrderGenerator

Generates synthetic shipping order data for the customer dataset
and stores the resulting orders in the Silver data layer.

Responsibilities:

* Generate multiple orders for each customer.
* Randomly assign orders to available warehouses.
* Generate realistic order attributes such as weight, size,
  priority, status, and creation date.
* Assign a unique UUID to each order.
* Return the generated data as a Polars DataFrame.
* Save the generated orders as a Parquet file in the Silver layer.

Order attributes:

* order_id
* customer_id
* warehouse_id
* package_weight_kg
* package_size
* priority
* status
* created_at

Workflow:
Customers + Warehouses
↓
OrderGenerator.generate()
↓
Synthetic order DataFrame
↓
OrderGenerator.save()
↓
Silver layer (orders.parquet)

The generated data is synthetic and intended for testing,
development, and downstream data pipeline processing.
"""
