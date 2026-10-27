"""Dialect-neutral schema model.

Every source (live introspection, DDL parsing, migrations) produces a `Schema`.
Diffing, linting, exporting and the UI work only with these objects.
The model describes structure only; it never holds table rows.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class Column(_Frozen):
    name: str
    type: str = Field(description="Type as declared in the source database, e.g. 'VARCHAR(80)'.")
    nullable: bool = True
    default: str | None = Field(default=None, description="Default expression as SQL text.")


class Index(_Frozen):
    name: str
    columns: list[str]
    unique: bool = False


class ForeignKey(_Frozen):
    columns: list[str]
    ref_table: str
    ref_columns: list[str]
    on_delete: str = "NO ACTION"
    on_update: str = "NO ACTION"


class Table(_Frozen):
    name: str
    columns: list[Column]
    primary_key: list[str] = Field(default_factory=list)
    indexes: list[Index] = Field(default_factory=list)
    foreign_keys: list[ForeignKey] = Field(default_factory=list)

    def column(self, name: str) -> Column | None:
        """Return the column called `name`, or None."""
        return next((c for c in self.columns if c.name == name), None)


class Schema(_Frozen):
    dialect: str
    source: str = Field(description="Where the schema came from, e.g. a file name.")
    captured_at: datetime
    tables: list[Table]

    def table(self, name: str) -> Table | None:
        """Return the table called `name`, or None."""
        return next((t for t in self.tables if t.name == name), None)
