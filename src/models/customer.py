"""
Customer model.

A flat, EU-based customer record for the synthetic shipping
operation. Replaces the nested RandomUser schema.
"""

from pydantic import BaseModel, ConfigDict, Field


class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_id: str = Field(..., description="Stable UUID")
    title: str
    first_name: str
    last_name: str
    gender: str
    email: str
    phone: str
    street_number: int
    street_name: str
    city: str
    state: str
    country: str
    postcode: str
    latitude: float
    longitude: float
    registered_date: str
    nationality: str
