from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from schemascope.model import Column, Schema, Table


def _schema() -> Schema:
    table = Table(name="t", columns=[Column(name="id", type="INTEGER")], primary_key=["id"])
    return Schema(
        dialect="sqlite", source="x", captured_at=datetime(2026, 1, 1, tzinfo=UTC), tables=[table]
    )


def test_lookup_helpers() -> None:
    schema = _schema()
    table = schema.table("t")
    assert table is not None
    assert table.column("id") is not None
    assert schema.table("nope") is None
    assert table.column("nope") is None


def test_json_round_trip() -> None:
    schema = _schema()
    assert Schema.model_validate_json(schema.model_dump_json()) == schema


def test_models_are_immutable() -> None:
    with pytest.raises(ValidationError):
        _schema().dialect = "postgres"  # type: ignore[misc]
