from pathlib import Path

import duckdb

from src.config.settings import DUCKDB_PATH, WAREHOUSE_TABLES
from src.utils.logger import logger


class WarehouseLoader:
    """
    Load parquet data into DuckDB.

    Usable as a context manager:

        with WarehouseLoader() as loader:
            loader.load_table("customers", path)
    """

    def __init__(self) -> None:
        self.connection = duckdb.connect(str(DUCKDB_PATH))
        logger.debug(f"Connected to DuckDB: {DUCKDB_PATH}")

    # -- context manager -------------------------------------------------

    def __enter__(self) -> "WarehouseLoader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # -- public API ------------------------------------------------------

    def load_table(self, table_name: str, parquet_path: str | Path) -> int:
        """
        Replace <table_name> in DuckDB with the contents of <parquet_path>.

        Returns the row count of the freshly loaded table.
        """
        if table_name not in WAREHOUSE_TABLES:
            raise ValueError(
                f"Refusing to load unregistered table: {table_name!r}. "
                f"Register it in settings.WAREHOUSE_TABLES first."
            )

        path_str = str(Path(parquet_path))

        # Parameterised path — avoids quoting/escaping issues.
        self.connection.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS "
            f"SELECT * FROM read_parquet(?)",
            [path_str],
        )

        row_count = self.connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        logger.info(f"Loaded {table_name}: {row_count} rows <- {path_str}")

        return row_count

    def close(self) -> None:
        self.connection.close()
        logger.debug("Closed DuckDB connection")
