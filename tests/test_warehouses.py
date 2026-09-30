import polars as pl

from src.extract.warehouses import WarehouseGenerator


def test_warehouse_generation():
    generator = WarehouseGenerator()

    warehouses = generator.generate()

    assert isinstance(
        warehouses,
        pl.DataFrame,
    )

    assert warehouses.height == 4


def test_warehouse_schema():
    generator = WarehouseGenerator()

    warehouses = generator.generate()

    expected_columns = {
        "warehouse_id",
        "name",
        "city",
        "country",
        "latitude",
        "longitude",
        "capacity",
    }

    assert expected_columns.issubset(set(warehouses.columns))


def test_warehouse_ids_are_unique():
    generator = WarehouseGenerator()

    warehouses = generator.generate()

    assert warehouses["warehouse_id"].n_unique() == warehouses.height


def test_generate_respects_count_argument():
    subset = WarehouseGenerator().generate(count=2)
    assert subset.height == 2
    assert set(subset["warehouse_id"]) == {"WH-001", "WH-002"}


def test_generate_rejects_excessive_count():
    import pytest

    with pytest.raises(ValueError, match="warehouses defined"):
        WarehouseGenerator().generate(count=999)
