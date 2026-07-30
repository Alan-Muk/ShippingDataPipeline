from src.extract.customers import CustomerExtractor
from src.transform.customers import CustomerTransformer
from src.utils.logger import logger
from src.extract.warehouses import WarehouseGenerator
from src.extract.weather import WeatherExtractor
from src.transform.delivery_risk import DeliveryRiskTransformer
from src.config.settings import SILVER_DIR, GOLD_DIR
from src.warehouse.load import WarehouseLoader

from src.extract.orders import OrderGenerator
from src.transform.routes import RouteTransformer
import polars as pl



def run_customer_pipeline():

    logger.info("Starting customer pipeline")

    # Customers
    extractor = CustomerExtractor()
    transformer = CustomerTransformer()

    raw_customers = extractor.fetch(100)

    extractor.save_raw(raw_customers)

    customers_df = transformer.transform(
        raw_customers
    )

    transformer.save(
        customers_df
    )


    # Warehouses
    warehouse_generator = WarehouseGenerator()

    warehouses_df = warehouse_generator.generate()

    warehouse_generator.save(
        warehouses_df
    )

    #Weather
    weather_extractor = WeatherExtractor()

    raw_weather = weather_extractor.fetch(
        warehouses_df
    )

    weather_extractor.save_raw(
        raw_weather
    )

    weather_df = weather_extractor.transform(
        raw_weather
    )

    weather_extractor.save(
        weather_df
    )


    # Orders
    order_generator = OrderGenerator()

    orders_df = order_generator.generate(
        customers_df,
        warehouses_df,
        orders_per_customer=3,
    )

    order_generator.save(
        orders_df
    )


    # Routes
    route_transformer = RouteTransformer()

    routes_df = route_transformer.transform(
        orders_df,
        customers_df,
        warehouses_df,
    )

    route_transformer.save(
        routes_df
    )

    # Delivery Risk

    risk_transformer = DeliveryRiskTransformer()

    weather_df = pl.read_parquet(
        SILVER_DIR
        / "weather"
        / "weather.parquet"
    )

    risk_df = risk_transformer.transform(
        routes_df,
        weather_df,
    )

    risk_transformer.save(
        risk_df
    )

    # Warehouse Load

    loader = WarehouseLoader()

    loader.load_table(
        "customers",
        str(
            SILVER_DIR
            / "customers"
            / "customers.parquet"
        ),
    )

    loader.load_table(
        "warehouses",
        str(
            SILVER_DIR
            / "warehouses"
            / "warehouses.parquet"
        ),
    )

    loader.load_table(
        "weather",
        str(
            SILVER_DIR
            / "weather"
            / "weather.parquet"
        ),
    )

    loader.load_table(
        "orders",
        str(
            SILVER_DIR
            / "orders"
            / "orders.parquet"
        ),
    )

    loader.load_table(
        "routes",
        str(
            GOLD_DIR
            / "routes"
            / "routes.parquet"
        ),
    )

    loader.load_table(
        "delivery_risk",
        str(
            GOLD_DIR
            / "delivery_risk"
            / "delivery_risk.parquet"
        ),
    )

    loader.close()

    logger.info(
        "Warehouse load complete"
    )

if __name__ == "__main__":
    run_customer_pipeline()