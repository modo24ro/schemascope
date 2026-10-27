import { ChangeEvent, useState } from "react";

import { inspectFile, loadDemo } from "./api";
import { columnBadges, describeForeignKey, filterTables, referencedBy } from "./schema";
import type { Schema } from "./types";

export default function App() {
  const [schema, setSchema] = useState<Schema | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");

  async function load(fetchSchema: () => Promise<Schema>) {
    setLoading(true);
    try {
      setSchema(await fetchSchema());
      setError(null);
    } catch (err) {
      setSchema(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) void load(() => inspectFile(file));
  }

  const tables = schema ? filterTables(schema.tables, query) : [];

  return (
    <main>
      <h1>SchemaScope</h1>
      <p className="tagline">Explore the structure of a SQLite database. Only the schema is read, never the data.</p>

      <div className="toolbar">
        <label className="file">
          Open SQLite file
          <input type="file" accept=".db,.sqlite,.sqlite3" onChange={onFile} />
        </label>
        <button type="button" onClick={() => void load(loadDemo)}>
          Load demo schema
        </button>
        {loading && <span className="muted">Loading…</span>}
      </div>

      {error && <p className="error">{error}</p>}

      {schema && (
        <>
          <div className="summary">
            <strong>{schema.source}</strong>
            <span className="muted">
              {schema.dialect} · {schema.tables.length} tables
            </span>
            <input
              type="search"
              placeholder="Filter tables or columns"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <div className="tables">
            {tables.map((table) => {
              const incoming = referencedBy(schema.tables, table.name);
              return (
                <section key={table.name} className="card">
                  <h2>{table.name}</h2>
                  <table>
                    <tbody>
                      {table.columns.map((column) => (
                        <tr key={column.name}>
                          <td className="mono">{column.name}</td>
                          <td className="mono muted">{column.type || "—"}</td>
                          <td>
                            {columnBadges(table, column).map((b) => (
                              <span key={b} className="badge">
                                {b}
                              </span>
                            ))}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {table.foreign_keys.map((fk) => (
                    <p key={describeForeignKey(fk)} className="relation mono">
                      FK {describeForeignKey(fk)}
                    </p>
                  ))}
                  {incoming.length > 0 && <p className="relation muted">Referenced by {incoming.join(", ")}</p>}
                </section>
              );
            })}
            {tables.length === 0 && <p className="muted">No tables match “{query}”.</p>}
          </div>
        </>
      )}
    </main>
  );
}
