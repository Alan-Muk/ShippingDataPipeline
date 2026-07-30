import duckdb

from src.config.settings import DUCKDB_PATH
from src.utils.logger import logger


class WarehouseLoader:
    """
    Load parquet data into DuckDB.
    """

    def __init__(self):
        self.connection = duckdb.connect(
            str(DUCKDB_PATH)
        )

    def load_table(
        self,
        table_name: str,
        parquet_path: str,
    ):
        query = f"""
        CREATE OR REPLACE TABLE {table_name}
        AS
        SELECT *
        FROM read_parquet('{parquet_path}');
        """

        self.connection.execute(query)

        logger.info(
            f"Loaded {table_name}"
        )

    def close(self):
        self.connection.close()