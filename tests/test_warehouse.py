from pathlib import Path

import duckdb

from src.warehouse.load import WarehouseLoader


def test_database_creation():

    loader = WarehouseLoader()

    assert loader.connection is not None

    loader.close()