"""Read the schema of a SQLite database.

Only catalog metadata is queried (``sqlite_schema`` and ``PRAGMA`` calls); table rows
are never read. File databases are opened read-only.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from schemascope.model import Column, ForeignKey, Index, Schema, Table

SQLITE_HEADER = b"SQLite format 3\x00"


class SchemaSourceError(Exception):
    """The input could not be read as a schema."""


def is_sqlite_file(path: Path) -> bool:
    """True when the file starts with the SQLite magic header."""
    try:
        with path.open("rb") as fh:
            return fh.read(len(SQLITE_HEADER)) == SQLITE_HEADER
    except OSError:
        return False


def introspect_file(path: str | Path, source: str | None = None) -> Schema:
    """Introspect a SQLite database file without modifying it."""
    path = Path(path)
    label = source or path.name
    if not path.is_file():
        raise SchemaSourceError(f"File not found: {path}")
    if not is_sqlite_file(path):
        raise SchemaSourceError(f"Not a SQLite database: {label}")
    uri = f"{path.resolve().as_uri()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        raise SchemaSourceError(f"Cannot open {label}: {exc}") from exc
    try:
        return introspect_connection(conn, source=label)
    except sqlite3.DatabaseError as exc:
        raise SchemaSourceError(f"Cannot read {label}: {exc}") from exc
    finally:
        conn.close()


def introspect_connection(conn: sqlite3.Connection, source: str) -> Schema:
    """Build a `Schema` from an open SQLite connection."""
    names = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_schema "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    tables = [_read_table(conn, name) for name in names]
    return Schema(dialect="sqlite", source=source, captured_at=datetime.now(UTC), tables=tables)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _read_table(conn: sqlite3.Connection, name: str) -> Table:
    q = _quote(name)
    # table_info rows: cid, name, type, notnull, dflt_value, pk (1-based position in the PK)
    info = conn.execute(f"PRAGMA table_info({q})").fetchall()
    columns = [
        Column(name=col, type=ctype, nullable=not notnull, default=default)
        for _cid, col, ctype, notnull, default, _pk in info
    ]
    pk = [col for _cid, col, *_rest, pos in sorted(info, key=lambda r: r[5]) if pos > 0]

    # index_list rows: seq, name, unique, origin ('c' = CREATE INDEX, 'u' = UNIQUE, 'pk'), partial
    indexes = []
    for row in conn.execute(f"PRAGMA index_list({q})").fetchall():
        idx_name, unique, origin = row[1], bool(row[2]), row[3]
        if origin == "pk":
            continue
        cols = [r[2] for r in conn.execute(f"PRAGMA index_info({_quote(idx_name)})").fetchall()]
        indexes.append(Index(name=idx_name, columns=cols, unique=unique))
    indexes.sort(key=lambda i: i.name)

    # foreign_key_list rows: id, seq, table, from, to, on_update, on_delete, match.
    # Rows sharing an id belong to one (possibly composite) key.
    grouped: dict[int, list[tuple]] = {}
    for row in conn.execute(f"PRAGMA foreign_key_list({q})").fetchall():
        grouped.setdefault(row[0], []).append(row)
    foreign_keys = []
    for fk_id in sorted(grouped):
        rows = sorted(grouped[fk_id], key=lambda r: r[1])
        ref_table = rows[0][2]
        foreign_keys.append(
            ForeignKey(
                columns=[r[3] for r in rows],
                ref_table=ref_table,
                # `to` is NULL when the key references the parent's primary key implicitly.
                ref_columns=[r[4] for r in rows if r[4] is not None]
                or _primary_key(conn, ref_table),
                on_update=rows[0][5],
                on_delete=rows[0][6],
            )
        )

    return Table(
        name=name, columns=columns, primary_key=pk, indexes=indexes, foreign_keys=foreign_keys
    )


def _primary_key(conn: sqlite3.Connection, table: str) -> list[str]:
    info = conn.execute(f"PRAGMA table_info({_quote(table)})").fetchall()
    return [r[1] for r in sorted(info, key=lambda r: r[5]) if r[5] > 0]
