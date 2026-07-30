from datetime import datetime
import json
import requests
from pathlib import Path

from src.utils.logger import logger
from src.config.settings import (RANDOM_USER_API,REQUEST_TIMEOUT,BRONZE_DIR)



class CustomerExtractor:
    BASE_URL = RANDOM_USER_API
    """
    Extract customer data from RandomUser API.
    """

    def fetch(self, count: int):

        logger.info(
            f"Fetching {count} customers"
        )

        params = {
            "results": count
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        return data

    def save_raw(self, data: dict) -> Path:
        """
        Save raw API response to Bronze layer.
        """

        output_dir = BRONZE_DIR / "customers"

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = output_dir / f"customers_{timestamp}.json"

        with open(output_file, "w") as file:
            json.dump(data, file, indent=2)

        logger.info(f"Saved raw customers: {output_file}")

        return output_file