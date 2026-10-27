import type { Column, ForeignKey, Table } from "./types";

/** Tables whose name, or one of whose column names, contains the query (case-insensitive). */
export function filterTables(tables: Table[], query: string): Table[] {
  const q = query.trim().toLowerCase();
  if (!q) return tables;
  return tables.filter(
    (t) => t.name.toLowerCase().includes(q) || t.columns.some((c) => c.name.toLowerCase().includes(q)),
  );
}

/** Short markers shown next to a column: PK, FK, NOT NULL. */
export function columnBadges(table: Table, column: Column): string[] {
  const badges: string[] = [];
  if (table.primary_key.includes(column.name)) badges.push("PK");
  if (table.foreign_keys.some((fk) => fk.columns.includes(column.name))) badges.push("FK");
  if (!column.nullable && !table.primary_key.includes(column.name)) badges.push("NOT NULL");
  return badges;
}

/** "(a, b) → other (x, y)" */
export function describeForeignKey(fk: ForeignKey): string {
  return `(${fk.columns.join(", ")}) → ${fk.ref_table} (${fk.ref_columns.join(", ")})`;
}

/** Names of tables that reference `table` through a foreign key. */
export function referencedBy(tables: Table[], table: string): string[] {
  return tables
    .filter((t) => t.foreign_keys.some((fk) => fk.ref_table === table))
    .map((t) => t.name);
}
