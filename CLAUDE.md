# CLAUDE.md

Notes for AI coding assistants working in this repository.

## Project

SchemaScope reads the structure of a database (tables, columns, keys, indexes) and
will diff, lint and draw it. It reads metadata only: no table rows, no user accounts,
no personal data. Keep it that way.

- `backend/schemascope/model.py` - dialect-neutral Pydantic models (`Schema`, `Table`, `Column`, ...)
- `backend/schemascope/sources/sqlite.py` - SQLite introspection (read-only, PRAGMA only)
- `backend/schemascope/demo.sql`, `demo.py` - synthetic demo schema
- `backend/schemascope/cli.py` - `schemascope inspect`, `schemascope serve` (argparse)
- `backend/schemascope/api.py` - FastAPI app (`/api/health`, `/api/demo`, `/api/inspect`)
- `frontend/src/` - React + TypeScript UI (Vite); `/api` is proxied to port 8000 in dev
- `frontend/src/types.ts` - hand-written mirror of the backend model

## Commands

```bash
cd backend && source .venv/bin/activate
pytest                      # tests
ruff check . && ruff format --check .

cd frontend
npm test                    # vitest
npm run build               # type-check + production build
```

## Conventions

- Python 3.11+, type hints everywhere, ruff line length 100.
- Every source returns a `Schema`; diff, lint, export and the UI use only the model,
  never SQL directly.
- Never add queries that read table rows. Open database files read-only.
- Test fixtures are synthetic schemas built from DDL in the tests; no real databases.
- When the backend model changes, update `frontend/src/types.ts` in the same change.
- Every behaviour change comes with a test; a bug fix starts with a failing test.
- No secrets, passwords or connection strings with real credentials in code, tests or docs.
- Add dependencies only when clearly needed.
- Planned work lives in `ROADMAP.md`; tick items off there when done.
