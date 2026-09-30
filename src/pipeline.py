"""
End-to-end ShippingDataPipeline runner.

Flow:
    customers ──► warehouses ──► weather ──► orders ──► routes ──► risk
                                                                │
                                                                ▼
                                                        DuckDB warehouse

Every step is a small, testable function. The top-level `run_pipeline`
returns a summary dict so callers (CLI, Airflow, tests) can inspect what
happened without re-parsing logs.
"""

from dataclasses import dataclass, field
from time import perf_counter

import polars as pl

from src.config.settings import (
    DEFAULT_CUSTOMER_COUNT,
    DEFAULT_ORDERS_PER_CUSTOMER,
    PIPELINE_SEED,
    SILVER_DIR,
    WAREHOUSE_TABLES,
    table_source_path,
)
from src.extract.customers import CustomerGenerator
from src.extract.orders import OrderGenerator
from src.extract.warehouses import WarehouseGenerator
from src.extract.weather import WeatherExtractor
from src.transform.customers import CustomerTransformer
from src.transform.delivery_risk import DeliveryRiskTransformer
from src.transform.routes import RouteTransformer
from src.utils.logger import logger
from src.warehouse.load import WarehouseLoader

# ---------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------


@dataclass
class StepResult:
    name: str
    duration_s: float
    rows: int | None = None
    path: str | None = None


@dataclass
class PipelineRun:
    steps: list[StepResult] = field(default_factory=list)

    def record(
        self,
        name: str,
        duration_s: float,
        rows: int | None = None,
        path: str | None = None,
    ) -> None:
        self.steps.append(StepResult(name, duration_s, rows, path))

    @property
    def total_duration_s(self) -> float:
        return sum(s.duration_s for s in self.steps)


# ---------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------


def _timed(run: PipelineRun, name: str, fn, *args, **kwargs):
    """Run fn(*args), time it, record it in the summary, return its result."""
    t0 = perf_counter()
    result = fn(*args, **kwargs)
    elapsed = perf_counter() - t0
    run.record(name, elapsed)
    return result


# ---------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------


def step_customers() -> pl.DataFrame:
    generator = CustomerGenerator()
    transformer = CustomerTransformer()

    raw = generator.fetch(DEFAULT_CUSTOMER_COUNT)
    generator.save_raw(raw)

    df = transformer.transform(raw)
    transformer.save(df)

    return df


def step_warehouses() -> pl.DataFrame:
    generator = WarehouseGenerator()
    df = generator.generate()
    generator.save(df)
    return df


def step_weather(warehouses_df: pl.DataFrame) -> pl.DataFrame:
    extractor = WeatherExtractor()
    raw = extractor.fetch(warehouses_df)
    extractor.save_raw(raw)

    df = extractor.transform(raw)
    extractor.save(df)

    return df


def step_orders(
    customers_df: pl.DataFrame,
    warehouses_df: pl.DataFrame,
) -> pl.DataFrame:
    generator = OrderGenerator()
    df = generator.generate(
        customers_df,
        warehouses_df,
        orders_per_customer=DEFAULT_ORDERS_PER_CUSTOMER,
    )
    generator.save(df)
    return df


def step_routes(
    orders_df: pl.DataFrame,
    customers_df: pl.DataFrame,
    warehouses_df: pl.DataFrame,
) -> pl.DataFrame:
    transformer = RouteTransformer()
    df = transformer.transform(orders_df, customers_df, warehouses_df)
    transformer.save(df)
    return df


def step_delivery_risk(
    routes_df: pl.DataFrame,
    weather_df: pl.DataFrame,
) -> pl.DataFrame:
    transformer = DeliveryRiskTransformer()
    df = transformer.transform(routes_df, weather_df)
    transformer.save(df)
    return df


def step_load_warehouse(run: PipelineRun) -> None:
    """Load every registered table from silver/gold into DuckDB."""
    with WarehouseLoader() as loader:
        for table_name in WAREHOUSE_TABLES:
            path = table_source_path(table_name)
            t0 = perf_counter()
            rows = loader.load_table(table_name, path)
            run.record(
                f"load:{table_name}", perf_counter() - t0, rows=rows, path=str(path)
            )


# ---------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------


def run_pipeline(seed: int | None = PIPELINE_SEED) -> PipelineRun:
    """
    Run the full end-to-end pipeline.

    `seed` controls reproducibility of synthetic data. None -> fresh data.
    """
    if seed is not None:
        import random, uuid

        random.seed(seed)
        logger.info(f"Pipeline seed set to {seed} for reproducibility")

    run = PipelineRun()
    logger.info("Starting shipping data pipeline")

    t0 = perf_counter()

    customers_df = _timed(run, "customers", step_customers)
    warehouses_df = _timed(run, "warehouses", step_warehouses)
    weather_df = _timed(run, "weather", step_weather, warehouses_df)
    orders_df = _timed(run, "orders", step_orders, customers_df, warehouses_df)
    routes_df = _timed(
        run, "routes", step_routes, orders_df, customers_df, warehouses_df
    )
    _timed(run, "delivery_risk", step_delivery_risk, routes_df, weather_df)

    step_load_warehouse(run)

    total = perf_counter() - t0
    logger.info(f"Pipeline finished in {total:.2f}s")

    for step in run.steps:
        rows = f"{step.rows} rows" if step.rows is not None else ""
        logger.info(f"  ✓ {step.name:<22} {step.duration_s:>6.2f}s  {rows}")

    return run


if __name__ == "__main__":
    run_pipeline()
