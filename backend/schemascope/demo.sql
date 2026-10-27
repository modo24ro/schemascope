-- Synthetic demo schema: a small inventory system. No real data.
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories (id) ON DELETE SET NULL
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    country_code CHAR(2) NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    sku VARCHAR(32) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories (id),
    supplier_id INTEGER REFERENCES suppliers (id),
    unit_price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1
);
CREATE INDEX ix_products_category ON products (category_id);

CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY,
    code VARCHAR(8) NOT NULL UNIQUE,
    city TEXT NOT NULL
);

CREATE TABLE stock_levels (
    warehouse_id INTEGER NOT NULL REFERENCES warehouses (id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (warehouse_id, product_id)
);

CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY,
    warehouse_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    reason TEXT NOT NULL DEFAULT 'adjustment',
    moved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id, product_id) REFERENCES stock_levels (warehouse_id, product_id)
);
CREATE INDEX ix_stock_movements_moved_at ON stock_movements (moved_at);
