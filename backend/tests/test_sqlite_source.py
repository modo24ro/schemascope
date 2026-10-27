from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from conftest import make_db

from schemascope.sources.sqlite import SchemaSourceError, introspect_file


def test_lists_tables_sorted_and_skips_internal(demo_db: Path) -> None:
    schema = introspect_file(demo_db)
    assert schema.dialect == "sqlite"
    assert schema.source == "demo.db"
    assert [t.name for t in schema.tables] == [
        "categories",
        "products",
        "stock_levels",
        "stock_movements",
        "suppliers",
        "warehouses",
    ]


def test_columns_types_nullability_defaults(demo_db: Path) -> None:
    products = introspect_file(demo_db).table("products")
    assert products is not None
    sku = products.column("sku")
    assert sku is not None and sku.type == "VARCHAR(32)" and not sku.nullable
    supplier = products.column("supplier_id")
    assert supplier is not None and supplier.nullable
    price = products.column("unit_price")
    assert price is not None and price.default == "0"
    assert [c.name for c in products.columns][:3] == ["id", "sku", "name"]


def test_composite_primary_key_keeps_order(demo_db: Path) -> None:
    stock = introspect_file(demo_db).table("stock_levels")
    assert stock is not None
    assert stock.primary_key == ["warehouse_id", "product_id"]


def test_foreign_keys_including_composite_and_self_reference(demo_db: Path) -> None:
    schema = introspect_file(demo_db)
    movements = schema.table("stock_movements")
    assert movements is not None
    (fk,) = movements.foreign_keys
    assert fk.columns == ["warehouse_id", "product_id"]
    assert fk.ref_table == "stock_levels"
    assert fk.ref_columns == ["warehouse_id", "product_id"]

    categories = schema.table("categories")
    assert categories is not None
    (parent,) = categories.foreign_keys
    assert (parent.ref_table, parent.ref_columns, parent.on_delete) == (
        "categories",
        ["id"],
        "SET NULL",
    )


def test_implicit_reference_to_parent_primary_key(tmp_path: Path) -> None:
    db = make_db(
        tmp_path / "implicit.db",
        "CREATE TABLE a (id INTEGER PRIMARY KEY);"
        "CREATE TABLE b (id INTEGER PRIMARY KEY, a_id INTEGER REFERENCES a);",
    )
    b = introspect_file(db).table("b")
    assert b is not None
    assert b.foreign_keys[0].ref_columns == ["id"]


def test_indexes_unique_and_plain(demo_db: Path) -> None:
    products = introspect_file(demo_db).table("products")
    assert products is not None
    by_name = {i.name: i for i in products.indexes}
    assert by_name["ix_products_category"].columns == ["category_id"]
    assert not by_name["ix_products_category"].unique
    assert any(i.unique and i.columns == ["sku"] for i in products.indexes)


def test_quoted_identifiers(tmp_path: Path) -> None:
    db = make_db(tmp_path / "quoted.db", 'CREATE TABLE "Order Items" ("Line ""No""" INT);')
    (table,) = introspect_file(db).tables
    assert table.name == "Order Items"
    assert table.columns[0].name == 'Line "No"'


def test_file_is_not_modified(demo_db: Path) -> None:
    before = hashlib.sha256(demo_db.read_bytes()).hexdigest()
    introspect_file(demo_db)
    assert hashlib.sha256(demo_db.read_bytes()).hexdigest() == before


def test_rejects_non_sqlite_file(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    with pytest.raises(SchemaSourceError, match="Not a SQLite database"):
        introspect_file(path)


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SchemaSourceError, match="File not found"):
        introspect_file(tmp_path / "missing.db")
