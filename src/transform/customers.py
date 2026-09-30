"""
CustomerTransformer

Validates and normalises synthetic customer records into a
Polars DataFrame, then persists to the Silver layer.
"""

from pathlib import Path

import polars as pl

from src.config.settings import SILVER_DIR
from src.models.customer import Customer
from src.utils.logger import logger


class CustomerTransformer:
    """Transform generated customer records into analytics-ready data."""

    def transform(self, raw_data: dict) -> pl.DataFrame:
        """Validate each record through Pydantic, then build a DataFrame."""
        records = [Customer(**record).model_dump() for record in raw_data["results"]]

        df = pl.DataFrame(records)

        logger.info(f"Transformed {df.height} customers")
        return df

    def save(self, df: pl.DataFrame) -> Path:
        output_dir = SILVER_DIR / "customers"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "customers.parquet"
        df.write_parquet(output_file)
        logger.info(f"Saved customers parquet: {output_file}")
        return output_file
