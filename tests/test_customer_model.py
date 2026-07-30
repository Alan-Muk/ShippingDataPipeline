from src.models.customer import Customer


def test_customer_model():
    customer = {
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
        "phone": "123456",
        "location": {
            "street": {
                "number": 1,
                "name": "Main Street"
            },
            "city": "London",
            "state": "London",
            "country": "UK",
            "postcode": "SW1A",
            "coordinates": {
                "latitude": 51.5,
                "longitude": -0.1
            }
        },
        "registered": {
            "date": "2024-01-01"
        },
        "nat": "GB"
    }

    result = Customer(**customer)

    assert result.email == "john@example.com"
    assert result.location.city == "London"