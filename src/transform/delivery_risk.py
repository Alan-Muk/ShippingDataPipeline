"""
DeliveryRiskTransformer

Computes a 0–100 delivery-risk score per route by combining
distance, estimated duration, and weather conditions at the
route's origin warehouse.

Scores are computed natively in Polars (no row-by-row loops).
Missing weather is treated as elevated risk rather than zero.
"""

from pathlib import Path

import polars as pl

from src.config.settings import GOLD_DIR
from src.utils.logger import logger

# ---------------------------------------------------------------------
# Risk thresholds
# ---------------------------------------------------------------------
# Each tier is (lower_bound_exclusive, points_awarded), sorted high→low.
# A value is awarded the points of the *highest* tier it clears.

DISTANCE_TIERS_KM: list[tuple[float, int]] = [(2_000, 15), (5_000, 25), (10_000, 35)]
DURATION_TIERS_H: list[tuple[float, int]] = [(12, 5), (24, 15), (36, 25)]
TEMPERATURE_TIERS_C: list[tuple[float, int]] = [(20, 10), (25, 20)]
WIND_TIERS_KMH: list[tuple[float, int]] = [(5, 5), (10, 15)]

# Penalty applied when weather is missing entirely for a route's warehouse.
UNKNOWN_WEATHER_PENALTY = 15

# Score cap (defensive — current max reachable is 100 exactly).
MAX_SCORE = 100

# Risk-level boundaries, highest first.
# Risk-level boundaries, low→high (evaluated in order; last match wins).
RISK_LEVELS: list[tuple[int, str]] = [
    (0, "LOW"),
    (25, "MEDIUM"),
    (50, "HIGH"),
    (65, "CRITICAL"),  # 65, not 70
]


class DeliveryRiskTransformer:
    """Create delivery risk analytics."""

    # ---- public API --------------------------------------------------

    def transform(
        self,
        routes: pl.DataFrame,
        weather: pl.DataFrame,
    ) -> pl.DataFrame:
        logger.info("Calculating delivery risk")

        # Latest weather observation per warehouse.
        #
        # NOTE: this is "current weather at pipeline run time",
        # not weather at order time. For production, replace with an
        # asof-join on (warehouse_id, order.created_at) — see README.
        latest_weather = (
            weather.sort("timestamp")
            .group_by("warehouse_id")
            .agg(
                pl.col("temperature").last().alias("temperature"),
                pl.col("wind_speed").last().alias("wind_speed"),
            )
        )

        enriched = routes.join(latest_weather, on="warehouse_id", how="left")

        scored = (
            enriched.with_columns(
                self._score_expr("distance_km", DISTANCE_TIERS_KM).alias(
                    "distance_points"
                ),
                self._score_expr("estimated_hours", DURATION_TIERS_H).alias(
                    "duration_points"
                ),
                self._score_expr("temperature", TEMPERATURE_TIERS_C)
                .fill_null(UNKNOWN_WEATHER_PENALTY)
                .alias("temperature_points"),
                self._score_expr("wind_speed", WIND_TIERS_KMH)
                .fill_null(UNKNOWN_WEATHER_PENALTY)
                .alias("wind_points"),
            )
            .with_columns(
                (
                    pl.col("distance_points")
                    + pl.col("duration_points")
                    + pl.col("temperature_points")
                    + pl.col("wind_points")
                )
                .clip(upper_bound=MAX_SCORE)
                .alias("risk_score")
            )
            .with_columns(self._risk_level_expr("risk_score").alias("risk_level"))
        )

        result = scored.select(
            "route_id",
            "order_id",
            "warehouse_id",
            "distance_km",
            "estimated_hours",
            "temperature",
            "wind_speed",
            "risk_score",
            "risk_level",
        )

        self._log_distribution(result)
        return result

    def save(self, df: pl.DataFrame) -> Path:
        output_dir = GOLD_DIR / "delivery_risk"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "delivery_risk.parquet"
        df.write_parquet(output_file)
        logger.info(f"Saved delivery risk: {output_file}")
        return output_file

    # ---- internals ---------------------------------------------------

    @staticmethod
    def _score_expr(column: str, tiers: list[tuple[float, int]]) -> pl.Expr:
        """Build a pl.when/then/otherwise chain from a high→low tier list."""
        expr = pl.lit(0, dtype=pl.Int32)
        for lower_bound, points in tiers:
            expr = (
                pl.when(pl.col(column) > lower_bound)
                .then(pl.lit(points, dtype=pl.Int32))
                .otherwise(expr)
            )
        return expr

    @staticmethod
    def _risk_level_expr(score_col: str) -> pl.Expr:
        expr = pl.lit("LOW")
        for threshold, label in RISK_LEVELS:  # high → low
            expr = (
                pl.when(pl.col(score_col) >= threshold)
                .then(pl.lit(label))
                .otherwise(expr)
            )
        return expr

    @staticmethod
    def _log_distribution(df: pl.DataFrame) -> None:
        dist = df.group_by("risk_level").len().sort("risk_level").to_dicts()
        scores = df["risk_score"]
        logger.info(
            f"Risk distribution: {dist} " f"(score range {scores.min()}–{scores.max()})"
        )
