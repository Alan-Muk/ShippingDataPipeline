"""
RouteTransformer

Builds shipping routes from orders, customers, and warehouses.

Distance is computed with the vectorised haversine great-circle
formula. Transport mode is assigned deterministically from
distance, and estimated duration is derived from a mode-specific
average speed plus fixed handling overhead.
"""

from pathlib import Path

import polars as pl

from src.config.settings import GOLD_DIR
from src.utils.logger import logger

# ---------------------------------------------------------------------
# Transport model
# ---------------------------------------------------------------------

EARTH_RADIUS_KM = 6371.0

# Mode assignment by straight-line distance (km), highest tier first.
# A route is assigned the first tier whose threshold it meets or exceeds.
MODE_DISTANCE_TIERS: list[tuple[float, str]] = [
    (0.0, "van"),
    (500.0, "truck"),
    (3_000.0, "air"),
]

# Average speed per mode (km/h) and fixed handling overhead (hours).
TRANSPORT_SPEEDS_KMH: dict[str, float] = {
    "van": 70.0,
    "truck": 55.0,
    "air": 800.0,
}

HANDLING_HOURS: dict[str, float] = {
    "van": 1.0,
    "truck": 2.0,
    "air": 12.0,
}


class RouteTransformer:
    """Create shipping routes from orders, customers, and warehouses."""

    # ---- public API --------------------------------------------------

    def transform(
        self,
        orders: pl.DataFrame,
        customers: pl.DataFrame,
        warehouses: pl.DataFrame,
    ) -> pl.DataFrame:
        logger.info("Building routes")

        enriched = (
            orders.join(
                customers.select("customer_id", "latitude", "longitude"),
                on="customer_id",
            )
            .rename(
                {
                    "latitude": "customer_latitude",
                    "longitude": "customer_longitude",
                }
            )
            .join(
                warehouses.select("warehouse_id", "latitude", "longitude"),
                on="warehouse_id",
            )
            .rename(
                {
                    "latitude": "warehouse_latitude",
                    "longitude": "warehouse_longitude",
                }
            )
        )

        # Distance → mode → duration, each depending on the previous.
        staged = (
            enriched.with_columns(
                self._haversine_expr(
                    "warehouse_latitude",
                    "warehouse_longitude",
                    "customer_latitude",
                    "customer_longitude",
                ).alias("distance_km")
            )
            .with_columns(
                self._transport_mode_expr("distance_km").alias("transport_mode")
            )
            .with_columns(
                self._estimated_hours_expr("distance_km", "transport_mode").alias(
                    "estimated_hours"
                )
            )
        )

        result = (
            staged.with_columns(
                pl.concat_str(
                    [
                        pl.lit("RT-"),
                        pl.col("order_id"),
                    ]
                ).alias("route_id")
            )
            .select(
                "route_id",
                "order_id",
                "customer_id",
                "warehouse_id",
                "distance_km",
                "estimated_hours",
                "transport_mode",
            )
            .with_columns(
                pl.col("distance_km").round(2),
                pl.col("estimated_hours").round(2),
            )
        )

        self._log_stats(result)
        return result

    def save(self, df: pl.DataFrame) -> Path:
        output_dir = GOLD_DIR / "routes"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "routes.parquet"
        df.write_parquet(output_file)
        logger.info(f"Saved routes: {output_file}")
        return output_file

    # ---- internals ---------------------------------------------------

    @staticmethod
    def _haversine_expr(
        lat1: str,
        lon1: str,
        lat2: str,
        lon2: str,
    ) -> pl.Expr:
        """Vectorised haversine — great-circle distance in km."""
        import math

        to_rad = math.pi / 180.0

        lat1_r = pl.col(lat1) * to_rad
        lon1_r = pl.col(lon1) * to_rad
        lat2_r = pl.col(lat2) * to_rad
        lon2_r = pl.col(lon2) * to_rad

        dlat = lat2_r - lat1_r
        dlon = lon2_r - lon1_r

        a = (dlat / 2).sin().pow(2) + lat1_r.cos() * lat2_r.cos() * (
            dlon / 2
        ).sin().pow(2)

        c = 2 * pl.arctan2(a.sqrt(), (1 - a).sqrt())

        return EARTH_RADIUS_KM * c

    @staticmethod
    def _transport_mode_expr(distance_col: str) -> pl.Expr:
        expr = pl.lit("van")
        for threshold, mode in MODE_DISTANCE_TIERS:  # high → low
            expr = (
                pl.when(pl.col(distance_col) >= threshold)
                .then(pl.lit(mode))
                .otherwise(expr)
            )
        return expr

    @staticmethod
    def _estimated_hours_expr(distance_col: str, mode_col: str) -> pl.Expr:
        expr = pl.lit(0.0)
        for mode, speed in TRANSPORT_SPEEDS_KMH.items():
            expr = (
                pl.when(pl.col(mode_col) == mode)
                .then(pl.col(distance_col) / speed + HANDLING_HOURS[mode])
                .otherwise(expr)
            )
        return expr

    @staticmethod
    def _log_stats(df: pl.DataFrame) -> None:
        d = df["distance_km"]
        h = df["estimated_hours"]
        modes = df["transport_mode"].value_counts().sort("transport_mode").to_dicts()

        logger.info(
            f"Routes: n={df.height}, "
            f"km [{d.min():.0f}–{d.max():.0f}] mean {d.mean():.0f}, "
            f"hrs [{h.min():.1f}–{h.max():.1f}] mean {h.mean():.1f}, "
            f"modes {modes}"
        )
