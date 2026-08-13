from pathlib import Path

import polars as pl

from src.config.settings import GOLD_DIR
from src.utils.logger import logger


class DeliveryRiskTransformer:
    """
    Create delivery risk analytics.
    """

    def calculate_risk_score(
        self,
        distance_km: float,
        estimated_hours: float,
        temperature: float,
        wind_speed: float,
    ) -> int:
        """
        Calculate risk score from route distance,
        delivery duration, and weather conditions.
        """

        score = 0

        # Distance risk
        if distance_km > 15000:
            score += 35
        elif distance_km > 10000:
            score += 25
        elif distance_km > 5000:
            score += 15

        # Delivery duration risk
        if estimated_hours > 250:
            score += 25
        elif estimated_hours > 100:
            score += 15

        # Temperature risk
        if temperature > 35:
            score += 20
        elif temperature > 30:
            score += 10

        # Wind risk
        if wind_speed > 20:
            score += 15
        elif wind_speed > 10:
            score += 5

        return min(score, 100)

    def risk_level(
        self,
        score: int,
    ) -> str:
        """
        Convert score to category.
        """

        if score >= 75:
            return "CRITICAL"

        if score >= 50:
            return "HIGH"

        if score >= 25:
            return "MEDIUM"

        return "LOW"

    def transform(
        self,
        routes: pl.DataFrame,
        weather: pl.DataFrame,
    ) -> pl.DataFrame:
        logger.info("Calculating delivery risk")

        enriched = routes.join(
            weather,
            on="warehouse_id",
            how="left",
        )

        records = []

        for row in enriched.iter_rows(named=True):
            score = self.calculate_risk_score(
                row["distance_km"],
                row["estimated_hours"],
                row["temperature"],
                row["wind_speed"],
            )

            records.append(
                {
                    "route_id": row["route_id"],
                    "order_id": row["order_id"],
                    "warehouse_id": row["warehouse_id"],
                    "distance_km": row["distance_km"],
                    "estimated_hours": row["estimated_hours"],
                    "temperature": row["temperature"],
                    "wind_speed": row["wind_speed"],
                    "risk_score": score,
                    "risk_level": self.risk_level(score),
                }
            )

        df = pl.DataFrame(records)

        logger.info(f"Generated {df.height} risk records")

        return df

    def save(
        self,
        df: pl.DataFrame,
    ) -> Path:
        output_dir = GOLD_DIR / "delivery_risk"

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_dir / "delivery_risk.parquet"

        df.write_parquet(output_file)

        logger.info(f"Saved delivery risk: {output_file}")

        return output_file
