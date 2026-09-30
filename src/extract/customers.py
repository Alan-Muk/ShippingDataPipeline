"""
CustomerGenerator

Generates synthetic EU-based customer records.

Replaces the RandomUser API extractor. The customer set is
deterministic given a fixed random seed.

Output is a dict shaped like the old API response:
    {"results": [<customer>, ...], "info": {...}}

so downstream transformers and bronze files remain unchanged.
"""

from datetime import datetime, timedelta
from pathlib import Path
import json
import random
import uuid

from src.config.settings import BRONZE_DIR, DEFAULT_CUSTOMER_COUNT
from src.utils.logger import logger

# ---------------------------------------------------------------------
# Reference data — EU cities with lat/lon for realistic geography
# ---------------------------------------------------------------------
# (city, state/region, country, latitude, longitude)
EU_CITIES: list[tuple[str, str, str, float, float]] = [
    ("Amsterdam", "North Holland", "Netherlands", 52.3676, 4.9041),
    ("Rotterdam", "South Holland", "Netherlands", 51.9244, 4.4777),
    ("Berlin", "Berlin", "Germany", 52.5200, 13.4050),
    ("Munich", "Bavaria", "Germany", 48.1351, 11.5820),
    ("Hamburg", "Hamburg", "Germany", 53.5511, 9.9937),
    ("Paris", "Île-de-France", "France", 48.8566, 2.3522),
    ("Lyon", "Auvergne-Rhône-Alpes", "France", 45.7640, 4.8357),
    ("Marseille", "Provence", "France", 43.2965, 5.3698),
    ("Madrid", "Madrid", "Spain", 40.4168, -3.7038),
    ("Barcelona", "Catalonia", "Spain", 41.3874, 2.1686),
    ("Valencia", "Valencia", "Spain", 39.4699, -0.3763),
    ("Rome", "Lazio", "Italy", 41.9028, 12.4964),
    ("Milan", "Lombardy", "Italy", 45.4642, 9.1900),
    ("Naples", "Campania", "Italy", 40.8518, 14.2681),
    ("Warsaw", "Masovia", "Poland", 52.2297, 21.0122),
    ("Krakow", "Lesser Poland", "Poland", 50.0647, 19.9450),
    ("Stockholm", "Stockholm", "Sweden", 59.3293, 18.0686),
    ("Gothenburg", "Västra Götaland", "Sweden", 57.7089, 11.9746),
    ("Vienna", "Vienna", "Austria", 48.2082, 16.3738),
    ("Brussels", "Brussels", "Belgium", 50.8503, 4.3517),
    ("Antwerp", "Flanders", "Belgium", 51.2194, 4.4025),
    ("Copenhagen", "Capital Region", "Denmark", 55.6761, 12.5683),
    ("Lisbon", "Lisbon", "Portugal", 38.7223, -9.1393),
    ("Porto", "Porto", "Portugal", 41.1579, -8.6291),
    ("Prague", "Prague", "Czechia", 50.0755, 14.4378),
    ("Budapest", "Budapest", "Hungary", 47.4979, 19.0402),
    ("Dublin", "Leinster", "Ireland", 53.3498, -6.2603),
    ("Helsinki", "Uusimaa", "Finland", 60.1699, 24.9384),
    ("Athens", "Attica", "Greece", 37.9838, 23.7275),
    ("Zurich", "Zurich", "Switzerland", 47.3769, 8.5417),
]

GENDERS = ["male", "female"]
TITLES = {
    "male": ["Mr", "Dr"],
    "female": ["Ms", "Mrs", "Dr"],
}
STREET_NAMES = [
    "Main",
    "High",
    "Church",
    "Park",
    "Station",
    "Market",
    "Kings",
    "Queens",
    "Victoria",
    "Albert",
    "New",
    "School",
]
STREET_SUFFIXES = ["Street", "Avenue", "Road", "Lane", "Square"]

FIRST_NAMES = {
    "male": [
        "Lucas",
        "Mateo",
        "Liam",
        "Noah",
        "Elias",
        "Hugo",
        "Adam",
        "Oscar",
        "Felix",
        "Jonas",
        "Milan",
        "Leo",
    ],
    "female": [
        "Emma",
        "Sofia",
        "Mia",
        "Anna",
        "Elena",
        "Clara",
        "Mila",
        "Lena",
        "Nora",
        "Julia",
        "Sara",
        "Iris",
    ],
}
LAST_NAMES = [
    "de Vries",
    "Jansen",
    "Müller",
    "Schmidt",
    "Rossi",
    "Ferrari",
    "García",
    "Martínez",
    "Dupont",
    "Martin",
    "Kowalski",
    "Nowak",
    "Andersson",
    "Johansson",
    "Novak",
    "Horvath",
    "O'Brien",
    "Murphy",
    "Virtanen",
    "Korhonen",
    "Papadopoulos",
    "Nikolaidis",
]


class CustomerGenerator:
    """Generate synthetic EU-based customers."""

    def fetch(self, count: int = DEFAULT_CUSTOMER_COUNT) -> dict:
        """
        Return a dict shaped like the old RandomUser response:
            {"results": [...], "info": {...}}
        """
        logger.info(f"Generating {count} EU customers")

        results = [self._make_customer() for _ in range(count)]

        return {
            "results": results,
            "info": {
                "seed": "synthetic-eu",
                "results": count,
                "generated_at": datetime.now().isoformat(),
            },
        }

    def save_raw(self, data: dict) -> Path:
        """Save the generated customer payload to the Bronze layer."""
        output_dir = BRONZE_DIR / "customers"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_file = output_dir / f"customers_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        logger.info(f"Saved raw customers: {output_file}")
        return output_file

    # ---- internals ---------------------------------------------------

    @staticmethod
    def _make_customer() -> dict:
        city, state, country, base_lat, base_lon = random.choice(EU_CITIES)

        gender = random.choice(GENDERS)
        first_name = random.choice(FIRST_NAMES[gender])
        last_name = random.choice(LAST_NAMES)

        # Jitter lat/lon by up to ~25km so customers within a city
        # don't share coordinates (important for realistic route distances)
        lat = round(base_lat + random.uniform(-0.25, 0.25), 4)
        lon = round(base_lon + random.uniform(-0.25, 0.25), 4)

        # Registration 1–7 years ago
        registered = datetime.now() - timedelta(days=random.randint(365, 365 * 7))

        return {
            "customer_id": str(uuid.uuid4()),
            "title": random.choice(TITLES[gender]),
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "email": f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@example.eu",
            "phone": f"+{random.randint(30, 49)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "street_number": random.randint(1, 250),
            "street_name": f"{random.choice(STREET_NAMES)} {random.choice(STREET_SUFFIXES)}",
            "city": city,
            "state": state,
            "country": country,
            "postcode": f"{random.randint(1000, 99999)}",
            "latitude": lat,
            "longitude": lon,
            "registered_date": registered.strftime("%Y-%m-%dT%H:%M:%S"),
            "nationality": country[:2].upper(),
        }
