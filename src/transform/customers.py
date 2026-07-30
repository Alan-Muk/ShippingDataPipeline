import polars as pl

from src.config.settings import SILVER_DIR
from src.models.customer import Customer
from src.utils.logger import logger


class CustomerTransformer:
    """
    Transform raw customer API responses into analytics-ready data.
    """

    def transform(self, raw_data: dict) -> pl.DataFrame:
        """
        Flatten RandomUser API response into a Polars DataFrame.
        """

        records = []

        for raw_customer in raw_data["results"]:

            customer = Customer(**raw_customer)

            records.append(
                {
                    "customer_id": customer.login.uuid,
                    "title": customer.name.title,
                    "first_name": customer.name.first,
                    "last_name": customer.name.last,
                    "gender": customer.gender,
                    "email": customer.email,
                    "phone": customer.phone,
                    "street_number": customer.location.street.number,
                    "street_name": customer.location.street.name,
                    "city": customer.location.city,
                    "state": customer.location.state,
                    "country": customer.location.country,
                    "postcode": str(customer.location.postcode),
                    "latitude": customer.location.coordinates.latitude,
                    "longitude": customer.location.coordinates.longitude,
                    "registered_date": customer.registered.date,
                    "nationality": customer.nat,
                }
            )

        df = pl.DataFrame(records)

        logger.info(
            f"Transformed {df.height} customers"
        )

        return df

    def save(self, df: pl.DataFrame) -> Path:
        """
        Save transformed customers to Silver layer.
        """

        output_dir = SILVER_DIR / "customers"

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = output_dir / "customers.parquet"

        df.write_parquet(output_file)

        logger.info(
            f"Saved customers parquet: {output_file}"
        )

        return output_file