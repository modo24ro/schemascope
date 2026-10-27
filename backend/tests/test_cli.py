from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemascope.cli import main


def test_inspect_text(demo_db: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["inspect", str(demo_db)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("demo.db (sqlite, 6 tables)")
    assert "  sku VARCHAR(32)  [NOT NULL]" in out
    assert "  FK (warehouse_id, product_id) -> stock_levels (warehouse_id, product_id)" in out


def test_inspect_json(demo_db: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["inspect", str(demo_db), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data["tables"]) == 6


def test_inspect_demo(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["inspect", "--demo"]) == 0
    assert capsys.readouterr().out.startswith("demo.sql (sqlite, 6 tables)")


def test_inspect_error_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["inspect", str(tmp_path / "missing.db")]) == 1
    assert "error: File not found" in capsys.readouterr().err
