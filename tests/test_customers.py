import polars as pl

from src.transform.customers import CustomerTransformer
from src.config.settings import (RANDOM_USER_API,REQUEST_TIMEOUT)

from src.extract.customers import CustomerExtractor

def test_customer_api_configuration():

    assert CustomerExtractor.BASE_URL == RANDOM_USER_API

def test_request_timeout_configuration():

    assert REQUEST_TIMEOUT > 0


def test_customer_transform_returns_dataframe():
    raw_data = {
        "results": [
            {
                "login": {
                    "uuid": "123"
                },
                "name": {
                    "title": "Mr",
                    "first": "John",
                    "last": "Smith"
                },
                "gender": "male",
                "email": "john@example.com",
                "phone": "123456789",
                "location": {
                    "street": {
                        "number": 1,
                        "name": "Main Street"
                    },
                    "city": "London",
                    "state": "London",
                    "country": "United Kingdom",
                    "postcode": "SW1A",
                    "coordinates": {
                        "latitude": "51.5074",
                        "longitude": "-0.1278"
                    }
                },
                "registered": {
                    "date": "2020-01-01T00:00:00Z"
                },
                "nat": "GB"
            }
        ]
    }

    transformer = CustomerTransformer()

    df = transformer.transform(raw_data)

    assert isinstance(df, pl.DataFrame)
    assert df.height == 1
    assert "customer_id" in df.columns
    assert "email" in df.columns