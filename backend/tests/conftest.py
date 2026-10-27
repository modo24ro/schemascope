from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from schemascope.demo import demo_ddl


def make_db(path: Path, ddl: str) -> Path:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(ddl)
    finally:
        conn.close()
    return path


@pytest.fixture
def demo_db(tmp_path: Path) -> Path:
    return make_db(tmp_path / "demo.db", demo_ddl())
