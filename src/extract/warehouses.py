from pathlib import Path

import polars as pl

from src.config.settings import SILVER_DIR
from src.utils.logger import logger


class WarehouseGenerator:
    """
    Generate warehouse reference data.
    """

    WAREHOUSES = [
        {
            "name": "Amsterdam Distribution Centre",
            "city": "Amsterdam",
            "country": "Netherlands",
            "latitude": 52.3676,
            "longitude": 4.9041,
            "capacity": 50000,
        },
        {
            "name": "Berlin Fulfilment Hub",
            "city": "Berlin",
            "country": "Germany",
            "latitude": 52.5200,
            "longitude": 13.4050,
            "capacity": 75000,
        },
        {
            "name": "Paris Logistics Centre",
            "city": "Paris",
            "country": "France",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "capacity": 60000,
        },
        {
            "name": "Madrid Shipping Hub",
            "city": "Madrid",
            "country": "Spain",
            "latitude": 40.4168,
            "longitude": -3.7038,
            "capacity": 45000,
        },
    ]

    def generate(self) -> pl.DataFrame:
        """
        Generate warehouse dataframe.
        """

        warehouses = []

        for index, warehouse in enumerate(
            self.WAREHOUSES,
            start=1,
        ):
            warehouses.append(
                {
                    "warehouse_id": f"WH-{index:03d}",
                    **warehouse,
                }
            )

        df = pl.DataFrame(warehouses)

        logger.info(
            f"Generated {df.height} warehouses"
        )

        return df

    def save(self, df: pl.DataFrame) -> Path:
        """
        Save warehouses to Silver layer.
        """

        output_dir = SILVER_DIR / "warehouses"

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_dir / "warehouses.parquet"

        df.write_parquet(output_file)

        logger.info(
            f"Saved warehouses parquet: {output_file}"
        )

        return output_file

"""
WarehouseGenerator

Generates warehouse reference data and stores the resulting
dataset in the Silver data layer.

Responsibilities:

* Define a fixed list of warehouse locations.
* Generate unique warehouse IDs using the WH-XXX format.
* Include warehouse details such as name, city, country,
  coordinates, and storage capacity.
* Return the generated warehouse data as a Polars DataFrame.
* Save the warehouse dataset as a Parquet file in the Silver layer.

Warehouse attributes:

* warehouse_id
* name
* city
* country
* latitude
* longitude
* capacity

Workflow:
Warehouse configuration
↓
WarehouseGenerator.generate()
↓
Warehouse reference DataFrame
↓
WarehouseGenerator.save()
↓
Silver layer (warehouses.parquet)

The warehouse data is static reference data intended to support
order generation and downstream data processing.
"""
