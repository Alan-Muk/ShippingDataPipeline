from datetime import datetime
import requests
import json
from pathlib import Path

import polars as pl


from src.utils.logger import logger
from src.config.settings import OPEN_METEO_API, BRONZE_DIR, SILVER_DIR, REQUEST_TIMEOUT


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

        for warehouse in warehouses_df.iter_rows(named=True):
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
                    "temperature": data["current_weather"]["temperature"],
                    "wind_speed": data["current_weather"]["windspeed"],
                }
            )

        logger.info(f"Fetched weather for {len(weather_records)} warehouses")

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

        filename = datetime.now().strftime("weather_%Y%m%d_%H%M%S.json")

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

        logger.info(f"Saved raw weather: {output_file}")

        return output_file

    def transform(
        self,
        data: list[dict],
    ) -> pl.DataFrame:
        """
        Convert weather records to dataframe.
        """

        df = pl.DataFrame(data)

        logger.info(f"Transformed {df.height} weather records")

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

        output_file = output_dir / "weather.parquet"

        df.write_parquet(output_file)

        logger.info(f"Saved weather parquet: {output_file}")

        return output_file


"""
WeatherExtractor

Extracts current weather data for each warehouse using the
Open-Meteo API and stores the results across the Bronze and
Silver data layers.

Responsibilities:

* Fetch current weather data using each warehouse's coordinates.
* Capture temperature, wind speed, warehouse ID, and timestamp.
* Save the raw weather records as timestamped JSON files
  in the Bronze layer.
* Transform the weather records into a Polars DataFrame.
* Save the transformed weather data as a Parquet file
  in the Silver layer.
* Support an optional output directory when saving the
  transformed weather data.

Weather attributes:

* warehouse_id
* timestamp
* temperature
* wind_speed

Workflow:
Warehouse coordinates
↓
Open-Meteo API
↓
WeatherExtractor.fetch()
↓
Raw weather records
↓
WeatherExtractor.save_raw()
↓
Bronze layer (JSON)
↓
WeatherExtractor.transform()
↓
Weather DataFrame
↓
WeatherExtractor.save()
↓
Silver layer (weather.parquet)

The extractor uses the warehouse latitude and longitude to
retrieve current weather conditions and preserves the raw
records before transforming them for downstream processing.
"""
