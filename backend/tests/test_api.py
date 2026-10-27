from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from schemascope import api
from schemascope.api import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/api/health").json()["status"] == "ok"


def test_demo() -> None:
    body = client.get("/api/demo").json()
    assert body["source"] == "demo.sql"
    assert len(body["tables"]) == 6


def test_inspect_upload(demo_db: Path) -> None:
    with demo_db.open("rb") as fh:
        response = client.post("/api/inspect", files={"file": ("shop.db", fh)})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "shop.db"
    assert {t["name"] for t in body["tables"]} >= {"products", "stock_levels"}


def test_inspect_rejects_non_sqlite() -> None:
    response = client.post("/api/inspect", files={"file": ("x.db", b"not a database")})
    assert response.status_code == 422
    assert "Not a SQLite database: x.db" in response.json()["detail"]


def test_inspect_strips_path_from_filename(demo_db: Path) -> None:
    with demo_db.open("rb") as fh:
        response = client.post("/api/inspect", files={"file": ("../../etc/shop.db", fh)})
    assert response.json()["source"] == "shop.db"


def test_inspect_rejects_large_upload(monkeypatch) -> None:
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 10)
    response = client.post("/api/inspect", files={"file": ("big.db", b"x" * 11)})
    assert response.status_code == 413
