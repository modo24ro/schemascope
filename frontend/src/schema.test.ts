import { describe, expect, it } from "vitest";

import { columnBadges, describeForeignKey, filterTables, referencedBy } from "./schema";
import type { Table } from "./types";

const col = (name: string, nullable = true) => ({ name, type: "INTEGER", nullable, default: null });

const products: Table = {
  name: "products",
  columns: [col("id", false), col("category_id", false), col("note")],
  primary_key: ["id"],
  indexes: [],
  foreign_keys: [
    { columns: ["category_id"], ref_table: "categories", ref_columns: ["id"], on_delete: "NO ACTION", on_update: "NO ACTION" },
  ],
};
const categories: Table = { name: "categories", columns: [col("id", false)], primary_key: ["id"], indexes: [], foreign_keys: [] };

describe("filterTables", () => {
  it("matches table and column names, ignoring case", () => {
    expect(filterTables([products, categories], "CATEG").map((t) => t.name)).toEqual(["products", "categories"]);
    expect(filterTables([products, categories], "note").map((t) => t.name)).toEqual(["products"]);
  });

  it("returns everything for an empty query", () => {
    expect(filterTables([products, categories], "  ")).toHaveLength(2);
  });
});

describe("columnBadges", () => {
  it("marks keys and required columns", () => {
    expect(columnBadges(products, products.columns[0])).toEqual(["PK"]);
    expect(columnBadges(products, products.columns[1])).toEqual(["FK", "NOT NULL"]);
    expect(columnBadges(products, products.columns[2])).toEqual([]);
  });
});

describe("relations", () => {
  it("describes a foreign key", () => {
    expect(describeForeignKey(products.foreign_keys[0])).toBe("(category_id) → categories (id)");
  });

  it("finds referencing tables", () => {
    expect(referencedBy([products, categories], "categories")).toEqual(["products"]);
    expect(referencedBy([products, categories], "products")).toEqual([]);
  });
});
