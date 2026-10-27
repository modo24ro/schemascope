// Mirrors backend/schemascope/model.py. Keep in sync until types are generated (see ROADMAP).

export interface Column {
  name: string;
  type: string;
  nullable: boolean;
  default: string | null;
}

export interface Index {
  name: string;
  columns: string[];
  unique: boolean;
}

export interface ForeignKey {
  columns: string[];
  ref_table: string;
  ref_columns: string[];
  on_delete: string;
  on_update: string;
}

export interface Table {
  name: string;
  columns: Column[];
  primary_key: string[];
  indexes: Index[];
  foreign_keys: ForeignKey[];
}

export interface Schema {
  dialect: string;
  source: string;
  captured_at: string;
  tables: Table[];
}
