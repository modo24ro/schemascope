"""Local HTTP API used by the React UI."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from schemascope import __version__
from schemascope.demo import demo_schema
from schemascope.model import Schema
from schemascope.sources.sqlite import SchemaSourceError, introspect_file

MAX_UPLOAD_BYTES = 20 * 1024 * 1024

app = FastAPI(title="SchemaScope", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/demo", response_model=Schema)
def demo() -> Schema:
    return demo_schema()


@app.post("/api/inspect", response_model=Schema)
async def inspect(file: UploadFile) -> Schema:
    """Introspect an uploaded SQLite file. The upload is deleted right after reading."""
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 20 MB.")
    source = Path(file.filename or "upload.db").name
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "upload.db"
        path.write_bytes(data)
        try:
            return introspect_file(path, source=source)
        except SchemaSourceError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
