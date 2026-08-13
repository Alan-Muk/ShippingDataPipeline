import polars as pl

from src.extract.weather import WeatherExtractor
from src.config.settings import OPEN_METEO_API, BRONZE_DIR, SILVER_DIR, REQUEST_TIMEOUT


def test_weather_api_configuration():
    assert WeatherExtractor.BASE_URL == OPEN_METEO_API


def test_weather_timeout_configuration():
    assert REQUEST_TIMEOUT > 0


def test_weather_transform():
    extractor = WeatherExtractor()

    data = [
        {
            "warehouse_id": "WH-001",
            "timestamp": "2026-07-29",
            "temperature": 20.5,
            "wind_speed": 10.2,
        }
    ]

    df = extractor.transform(data)

    assert isinstance(
        df,
        pl.DataFrame,
    )

    assert df.height == 1

    assert "temperature" in df.columns


def test_weather_schema():
    extractor = WeatherExtractor()

    df = extractor.transform(
        [
            {
                "warehouse_id": "WH-001",
                "timestamp": "2026-07-29",
                "temperature": 20,
                "wind_speed": 5,
            }
        ]
    )

    expected = {
        "warehouse_id",
        "timestamp",
        "temperature",
        "wind_speed",
    }

    assert expected.issubset(set(df.columns))


def test_save_weather(tmp_path):
    extractor = WeatherExtractor()

    df = pl.DataFrame(
        {
            "latitude": [40.7128],
            "longitude": [-74.0060],
            "temperature": [25.0],
        }
    )

    saved_file = extractor.save(
        df,
        output_dir=tmp_path,
    )

    assert saved_file.exists()
    assert saved_file.suffix == ".parquet"

    loaded = pl.read_parquet(saved_file)

    assert loaded.shape == df.shape
