import math
import random
from pathlib import Path

import polars as pl

from src.config.settings import GOLD_DIR
from src.utils.logger import logger


class RouteTransformer:
    """
    Create shipping routes from orders,
    customers, and warehouses.
    """

    TRANSPORT_MODES = [
        "truck",
        "van",
        "air",
    ]

    def haversine(
        self,
        lat1,
        lon1,
        lat2,
        lon2,
    ):
        """
        Calculate distance between two coordinates.
        """

        radius = 6371  # Earth radius in km

        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)

        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return radius * c

    def transform(
        self,
        orders: pl.DataFrame,
        customers: pl.DataFrame,
        warehouses: pl.DataFrame,
    ) -> pl.DataFrame:
        logger.info("Building routes")

        enriched = (
            orders.join(
                customers.select(
                    [
                        "customer_id",
                        "latitude",
                        "longitude",
                    ]
                ),
                on="customer_id",
            )
            .rename(
                {
                    "latitude": "customer_latitude",
                    "longitude": "customer_longitude",
                }
            )
            .join(
                warehouses.select(
                    [
                        "warehouse_id",
                        "latitude",
                        "longitude",
                    ]
                ),
                on="warehouse_id",
            )
            .rename(
                {
                    "latitude": "warehouse_latitude",
                    "longitude": "warehouse_longitude",
                }
            )
        )

        routes = []

        for row in enriched.iter_rows(named=True):
            distance = self.haversine(
                row["warehouse_latitude"],
                row["warehouse_longitude"],
                row["customer_latitude"],
                row["customer_longitude"],
            )

            routes.append(
                {
                    "route_id": f"RT-{random.randint(100000,999999)}",
                    "order_id": row["order_id"],
                    "customer_id": row["customer_id"],
                    "warehouse_id": row["warehouse_id"],
                    "distance_km": round(distance, 2),
                    "estimated_hours": round(
                        distance / 60,
                        2,
                    ),
                    "transport_mode": random.choice(self.TRANSPORT_MODES),
                }
            )

        df = pl.DataFrame(routes)

        logger.info(f"Generated {df.height} routes")

        return df

    def save(self, df: pl.DataFrame) -> Path:
        output_dir = GOLD_DIR / "routes"

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_dir / "routes.parquet"

        df.write_parquet(output_file)

        logger.info(f"Saved routes: {output_file}")

        return output_file
