# SchemaScope

Explore, diff and lint database schemas.

Point SchemaScope at a database and it shows you its structure: tables, columns,
types, primary keys, foreign keys and indexes. It reads **only the schema**
(catalog metadata), never the rows, and opens database files read-only.

SchemaScope is a Python library + CLI + FastAPI backend with a React + TypeScript
frontend.

## Status

Early stage (v0.1). SQLite introspection, a text/JSON CLI and a simple web UI work
today. PostgreSQL, DDL parsing, an interactive ER diagram, schema diffs, migration
generation and a design linter are planned in [ROADMAP.md](ROADMAP.md).

## Quick start

Requirements: Python 3.11+, Node.js 20+.

```bash
# Backend + CLI
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

schemascope inspect --demo            # built-in demo schema
schemascope inspect path/to/app.db    # your own SQLite file
schemascope inspect app.db --json     # machine-readable output
schemascope serve                     # API on http://127.0.0.1:8000 (docs at /docs)

# Frontend (http://localhost:5173), in a second terminal
cd frontend
npm install
npm run dev
```

Example output:

```text
demo.sql (sqlite, 6 tables)

categories
  id INTEGER  [PK]
  name TEXT  [NOT NULL]
  parent_id INTEGER
  FK (parent_id) -> categories (id)
...
```

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Status and version |
| `GET` | `/api/demo` | Schema of the built-in demo database |
| `POST` | `/api/inspect` | Multipart upload of a SQLite file (max 20 MB); returns its schema |

The uploaded file is written to a temporary directory, opened read-only and deleted
right after the schema is read. Invalid files return `422`.

## Privacy and safety

- Only metadata is queried (`sqlite_schema`, `PRAGMA table_info`, `index_list`,
  `foreign_key_list`); table data is never selected.
- Database files are opened with `mode=ro`.
- `schemascope serve` binds to `127.0.0.1` only.

## Development

```bash
cd backend && pytest && ruff check . && ruff format --check .
cd frontend && npm test && npm run build
```

CI runs the same checks on every push and pull request.

## License

[MIT](LICENSE) © 2026 Marius Odobasa
