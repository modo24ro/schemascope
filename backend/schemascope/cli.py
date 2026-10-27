"""Command-line interface: ``schemascope inspect``, ``schemascope serve``."""

from __future__ import annotations

import argparse
import sys

from schemascope import __version__
from schemascope.demo import demo_schema
from schemascope.model import Schema, Table
from schemascope.sources.sqlite import SchemaSourceError, introspect_file


def format_table(table: Table) -> list[str]:
    """Human-readable lines for one table."""
    lines = [table.name]
    for col in table.columns:
        flags = []
        if col.name in table.primary_key:
            flags.append("PK")
        if not col.nullable:
            flags.append("NOT NULL")
        if col.default is not None:
            flags.append(f"DEFAULT {col.default}")
        suffix = f"  [{', '.join(flags)}]" if flags else ""
        lines.append(f"  {col.name} {col.type or '(no type)'}{suffix}")
    for fk in table.foreign_keys:
        lines.append(
            f"  FK ({', '.join(fk.columns)}) -> {fk.ref_table} ({', '.join(fk.ref_columns)})"
        )
    for idx in table.indexes:
        kind = "UNIQUE INDEX" if idx.unique else "INDEX"
        lines.append(f"  {kind} {idx.name} ({', '.join(idx.columns)})")
    return lines


def format_schema(schema: Schema) -> str:
    out = [f"{schema.source} ({schema.dialect}, {len(schema.tables)} tables)", ""]
    for table in schema.tables:
        out.extend(format_table(table))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="schemascope", description=__doc__)
    parser.add_argument("--version", action="version", version=f"schemascope {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="print the schema of a SQLite database")
    target = inspect.add_mutually_exclusive_group(required=True)
    target.add_argument("path", nargs="?", help="path to a SQLite database file")
    target.add_argument("--demo", action="store_true", help="use the built-in demo schema")
    inspect.add_argument("--json", action="store_true", help="print JSON instead of text")

    serve = sub.add_parser("serve", help="start the local API (and UI in development)")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "inspect":
        try:
            schema = demo_schema() if args.demo else introspect_file(args.path)
        except SchemaSourceError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(schema.model_dump_json(indent=2) if args.json else format_schema(schema), end="")
        if args.json:
            print()
        return 0

    if args.command == "serve":
        import uvicorn

        # Bind to loopback only: the server is a local tool, not a public service.
        uvicorn.run("schemascope.api:app", host="127.0.0.1", port=args.port)
        return 0

    return 2  # unreachable: argparse enforces a command


if __name__ == "__main__":
    raise SystemExit(main())
