"""Built-in demo schema, so the tool can be tried without a database of your own."""

from __future__ import annotations

import sqlite3
from importlib.resources import files

from schemascope.model import Schema
from schemascope.sources.sqlite import introspect_connection


def demo_ddl() -> str:
    return files("schemascope").joinpath("demo.sql").read_text(encoding="utf-8")


def demo_schema() -> Schema:
    """Load the demo DDL into an in-memory SQLite database and introspect it."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(demo_ddl())
        return introspect_connection(conn, source="demo.sql")
    finally:
        conn.close()
