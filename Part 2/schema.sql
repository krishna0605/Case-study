CREATE TABLE companies (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE warehouses (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_warehouses_company_id ON warehouses(company_id);

CREATE TABLE product_types (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    low_stock_threshold INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    product_type_id BIGINT NOT NULL REFERENCES product_types(id),
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price NUMERIC(12, 2) NOT NULL,
    is_bundle BOOLEAN NOT NULL DEFAULT FALSE,
    override_low_stock_threshold INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_products_sku ON products(sku);

CREATE TABLE inventory_levels (
    product_id BIGINT NOT NULL REFERENCES products(id),
    warehouse_id BIGINT NOT NULL REFERENCES warehouses(id),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (product_id, warehouse_id)
);

CREATE TABLE inventory_movements (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(id),
    warehouse_id BIGINT NOT NULL REFERENCES warehouses(id),
    quantity_delta INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    reference_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_inventory_movements_lookup
    ON inventory_movements(product_id, warehouse_id, created_at DESC);

CREATE TABLE suppliers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE company_suppliers (
    company_id BIGINT NOT NULL REFERENCES companies(id),
    supplier_id BIGINT NOT NULL REFERENCES suppliers(id),
    account_number VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (company_id, supplier_id)
);

CREATE TABLE company_supplier_products (
    company_id BIGINT NOT NULL REFERENCES companies(id),
    product_id BIGINT NOT NULL REFERENCES products(id),
    supplier_id BIGINT NOT NULL REFERENCES suppliers(id),
    supplier_sku VARCHAR(100),
    unit_cost NUMERIC(12, 2),
    is_preferred BOOLEAN NOT NULL DEFAULT FALSE,
    lead_time_days INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (company_id, product_id, supplier_id),
    FOREIGN KEY (company_id, supplier_id)
        REFERENCES company_suppliers(company_id, supplier_id)
);
CREATE INDEX idx_company_supplier_products_lookup
    ON company_supplier_products(company_id, product_id, is_preferred);
CREATE UNIQUE INDEX idx_company_supplier_products_preferred
    ON company_supplier_products(company_id, product_id)
    WHERE is_preferred = TRUE;

CREATE TABLE bundle_components (
    bundle_product_id BIGINT NOT NULL REFERENCES products(id),
    component_product_id BIGINT NOT NULL REFERENCES products(id),
    component_quantity INTEGER NOT NULL CHECK (component_quantity > 0),
    PRIMARY KEY (bundle_product_id, component_product_id),
    CHECK (bundle_product_id <> component_product_id)
);

CREATE TABLE sales_order_items (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(id),
    warehouse_id BIGINT NOT NULL REFERENCES warehouses(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    sold_at TIMESTAMP NOT NULL
);
CREATE INDEX idx_sales_order_items_recent
    ON sales_order_items(product_id, warehouse_id, sold_at DESC);
