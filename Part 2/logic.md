# Part 2: Database Design

## 1. Design Schema

The schema is provided in [schema.sql](C:/Users/ADMIN/Desktop/Bynry%20-%20Case%20study%20submission/Part%202/schema.sql).

### Relationships

- One company can have many warehouses.
- One product can be stored in many warehouses through `inventory_levels`.
- `inventory_movements` tracks inventory changes over time.
- Suppliers provide products to companies through company-scoped mapping tables.
- Bundles are modeled through `bundle_components`.

## 2. Identify Gaps

1. What time window counts as recent sales activity?
2. Should low-stock alerts be per warehouse or aggregated across all warehouses for a company?
3. Can a product override the product-type threshold?
4. Can a warehouse override thresholds based on local demand?
5. Can multiple suppliers exist for the same company-product relationship?
6. If multiple suppliers exist, how should the preferred reorder supplier be selected?
7. Should reserved, damaged, or backordered stock reduce available inventory?
8. Should inactive or discontinued products appear in alerts?
9. For bundles, should stock be tracked directly, from components, or both?

## 3. Explain Decisions

- `products.sku` is unique because the prompt says SKUs must be unique across the platform.
- `inventory_levels` uses `(product_id, warehouse_id)` as a composite key so there is only one current stock row per product and warehouse.
- `inventory_movements` is separated from current inventory to support both operational reads and audit history.
- Company-scoped supplier mapping is used because suppliers provide products to companies, not just to the platform in general.
- A partial unique index on preferred supplier mappings prevents ambiguous preferred reorder suppliers.
- `sales_order_items` is included because the low-stock endpoint depends on recent sales activity.
