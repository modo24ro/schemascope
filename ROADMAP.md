# Roadmap

Planned work, roughly in priority order. Each item is meant to be a self-contained
change with tests.

## Sources

- [ ] PostgreSQL introspection (`information_schema` + `pg_catalog`), read-only connection
- [ ] Multiple namespaces (PostgreSQL schemas) in the model
- [ ] Parse DDL files (`CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX`) with sqlglot
- [ ] Same schema read from DDL and from a live database produces the same model (test)
- [ ] MySQL / MariaDB introspection
- [ ] DuckDB and SQL Server introspection
- [ ] Read Alembic and Django migrations (without running them against data)
- [ ] `SchemaSource` protocol + registry instead of per-dialect code paths
- [ ] Mask passwords in connection URLs in logs and error messages

## Model

- [ ] Views, check constraints, partial indexes (`WHERE`), generated columns
- [ ] Normalised column types (`kind`, length, precision, scale) next to the raw type
- [ ] Table and column comments
- [ ] Versioned JSON snapshot format (`schemascope snapshot`), loadable later

## Diff and migrations

- [ ] Diff two schemas: added / dropped / changed tables, columns, indexes, foreign keys
- [ ] Mark breaking changes (dropped column, narrowed type, new NOT NULL without default)
- [ ] Detect column renames by similarity, behind an option
- [ ] Generate PostgreSQL migration SQL from a diff
- [ ] Correct statement order for circular foreign keys
- [ ] Round-trip property test (Hypothesis): old schema + generated migration = new schema
- [ ] `schemascope diff old.db new.db` with text and JSON output

## Linter

- [ ] Rules: foreign key without index, table without primary key, naming conventions,
      FK/PK type mismatch, duplicate indexes, suspicious nullable columns
- [ ] Configuration in `schemascope.toml` (enable, severity, ignore)
- [ ] `schemascope lint` exit codes for CI, SARIF output
- [ ] GitHub Action that annotates pull requests
- [ ] Autofix for "foreign key without index" (emit `CREATE INDEX`)
- [ ] Plugin system for rules (entry points)

## Export

- [ ] Mermaid `erDiagram`
- [ ] Markdown documentation (one section per table)
- [ ] DBML and PlantUML
- [ ] Static documentation site

## Frontend

- [ ] Interactive ER diagram (React Flow + elkjs auto-layout): zoom, pan, drag
- [ ] Table details side panel; highlight search matches in the diagram
- [ ] Self-referencing foreign keys drawn as loops, not over the node
- [ ] Diff view: added / removed / changed tables coloured on the diagram
- [ ] Lint results panel
- [ ] Smooth rendering with 300+ tables
- [ ] Dark mode, saved layout per schema, export PNG/SVG
- [ ] Generate `types.ts` from the Pydantic models' JSON Schema
- [ ] Component tests with React Testing Library; Playwright end-to-end tests

## CLI and packaging

- [ ] Move CLI to Typer + Rich (colours, tables)
- [ ] `schemascope serve` serves the built UI from the Python package
- [ ] Random per-start token for the local API
- [ ] `watch` mode: refresh when DDL files change
- [ ] Publish to PyPI via Trusted Publishing; Docker image
- [ ] CI matrix: Python 3.11-3.13 on Linux, macOS, Windows; mypy --strict

## Docs

- [ ] README GIF and screenshots
- [ ] MkDocs site with a page per lint rule
- [ ] `CONTRIBUTING.md`, architecture decision records in `docs/decisions/`
