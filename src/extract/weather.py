from datetime import datetime
import requests
import json
from pathlib import Path

import polars as pl


from src.utils.logger import logger
from src.config.settings import (OPEN_METEO_API,BRONZE_DIR,SILVER_DIR,REQUEST_TIMEOUT)



class WeatherExtractor:
    """
    Extract weather data from Open-Meteo API.
    """

    BASE_URL = OPEN_METEO_API

    def fetch(
        self,
        warehouses_df: pl.DataFrame,
        ) -> list[dict]:
        """
        Fetch weather for each warehouse.
        """

        weather_records = []

        for warehouse in warehouses_df.iter_rows(
            named=True
        ):

            params = {
                "latitude": warehouse["latitude"],
                "longitude": warehouse["longitude"],
                "current_weather": True,
            }

            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            weather_records.append(
                {
                    "warehouse_id": warehouse["warehouse_id"],
                    "timestamp": datetime.now(),
                    "temperature": data["current_weather"][
                        "temperature"
                    ],
                    "wind_speed": data["current_weather"][
                        "windspeed"
                    ],
                }
            )

        logger.info(
            f"Fetched weather for {len(weather_records)} warehouses"
        )

        return weather_records

    def save_raw(
        self,
        data: list[dict],
        ) -> Path:
        """
        Save raw weather response.
        """

        output_dir = BRONZE_DIR / "weather"

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            datetime.now()
            .strftime(
                "weather_%Y%m%d_%H%M%S.json"
            )
        )

        output_file = output_dir / filename

        with open(
            output_file,
            "w",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                default=str,
            )

        logger.info(
            f"Saved raw weather: {output_file}"
        )

        return output_file

    def transform(
        self,
        data: list[dict],
        ) -> pl.DataFrame:
        """
        Convert weather records to dataframe.
        """

        df = pl.DataFrame(data)

        logger.info(
            f"Transformed {df.height} weather records"
        )

        return df

    def save(
        self,
        df: pl.DataFrame,
        output_dir: Path | None = None,
        ) -> Path:
        """
        Save weather parquet.
        """

        output_dir = output_dir or (SILVER_DIR / "weather")

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_dir / "weather.parquet"
        )

        df.write_parquet(
            output_file
        )

        logger.info(
            f"Saved weather parquet: {output_file}"
        )

        return output_file