"""
Tests for WarehouseLoader.
"""

from pathlib import Path

import polars as pl
import pytest

from src.warehouse.load import WarehouseLoader


@pytest.fixture
def sample_parquet(tmp_path) -> Path:
    """A tiny parquet file for load_table round-trip tests."""
    df = pl.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["a", "b", "c"],
        }
    )
    path = tmp_path / "sample.parquet"
    df.write_parquet(path)
    return path


@pytest.fixture
def registered_loader(sandbox_duckdb, monkeypatch):
    """
    A WarehouseLoader pointed at a temp DuckDB file, with a dummy
    table name registered in the whitelist so load_table() will
    accept it.
    """
    from src.warehouse import load as load_module

    monkeypatch.setitem(
        load_module.WAREHOUSE_TABLES,
        "test_table",
        ("silver", "test_table", "test_table.parquet"),
    )
    return WarehouseLoader()


# ---------------------------------------------------------------------
# Connection lifecycle
# ---------------------------------------------------------------------


def test_loader_opens_connection(sandbox_duckdb):
    loader = WarehouseLoader()
    try:
        assert loader.connection is not None
    finally:
        loader.close()


def test_context_manager_closes_connection(sandbox_duckdb):
    with WarehouseLoader() as loader:
        con = loader.connection

    with pytest.raises(Exception):
        con.execute("SELECT 1").fetchall()


# ---------------------------------------------------------------------
# load_table
# ---------------------------------------------------------------------


def test_load_table_returns_row_count(registered_loader, sample_parquet):
    rows = registered_loader.load_table("test_table", sample_parquet)
    assert rows == 3


def test_load_table_rejects_unregistered_name(registered_loader, sample_parquet):
    with pytest.raises(ValueError, match="unregistered table"):
        registered_loader.load_table("not_registered", sample_parquet)


def test_load_table_replaces_existing_data(registered_loader, tmp_path):
    v1 = pl.DataFrame({"id": [1, 2, 3]})
    v2 = pl.DataFrame({"id": [10, 20]})

    p1 = tmp_path / "v1.parquet"
    v1.write_parquet(p1)
    p2 = tmp_path / "v2.parquet"
    v2.write_parquet(p2)

    assert registered_loader.load_table("test_table", p1) == 3
    assert registered_loader.load_table("test_table", p2) == 2
