# Bynry Backend Engineering Case Study

This repository contains a structured submission for the Bynry backend engineering case study. The solution is organized by assessment part so each deliverable is easy to review independently.

## Repository Layout

- `Part 1/`
  - `code.py`: corrected product creation endpoint
  - `logic.md`: issue analysis, production impact, and fixes
- `Part 2/`
  - `schema.sql`: proposed database schema
  - `logic.md`: requirement gaps and design decisions
- `Part 3/`
  - `app.py`: runnable low-stock alerts API
  - `logic.md`: approach, edge cases, and assumptions
- `tests/`: API verification tests
- `requirements.txt`: Python dependencies

## Run Part 3

```powershell
cd "C:\Users\ADMIN\Desktop\Bynry - Case study submission"
python ".\Part 3\app.py"
```

API endpoint:

`GET /api/companies/{company_id}/alerts/low-stock`

Example:

[http://127.0.0.1:5000/api/companies/1/alerts/low-stock](http://127.0.0.1:5000/api/companies/1/alerts/low-stock)

## Run Tests

```powershell
cd "C:\Users\ADMIN\Desktop\Bynry - Case study submission"
pytest
```

## Diagrams

### Schema / Entity Relationship Map

```mermaid
erDiagram
    COMPANIES ||--o{ WAREHOUSES : owns
    PRODUCT_TYPES ||--o{ PRODUCTS : classifies
    PRODUCTS ||--o{ INVENTORY_LEVELS : stocked_as
    WAREHOUSES ||--o{ INVENTORY_LEVELS : stores
    PRODUCTS ||--o{ INVENTORY_MOVEMENTS : changes
    WAREHOUSES ||--o{ INVENTORY_MOVEMENTS : logs
    COMPANIES ||--o{ COMPANY_SUPPLIERS : approves
    SUPPLIERS ||--o{ COMPANY_SUPPLIERS : serves
    COMPANIES ||--o{ COMPANY_SUPPLIER_PRODUCTS : reorders
    PRODUCTS ||--o{ COMPANY_SUPPLIER_PRODUCTS : sourced_for
    SUPPLIERS ||--o{ COMPANY_SUPPLIER_PRODUCTS : fulfills
    PRODUCTS ||--o{ BUNDLE_COMPONENTS : bundle_parent
    PRODUCTS ||--o{ BUNDLE_COMPONENTS : bundle_component
    PRODUCTS ||--o{ SALES_ORDER_ITEMS : sold_as
    WAREHOUSES ||--o{ SALES_ORDER_ITEMS : fulfilled_from
```

### Low-Stock Alert Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as LowStock API
    participant DB as Repository

    Client->>API: GET /api/companies/{company_id}/alerts/low-stock
    API->>DB: Validate company and fetch warehouses
    API->>DB: Read recent sales for last 30 days
    API->>DB: Join inventory, product, threshold, supplier
    API->>API: Compute days_until_stockout
    API->>Client: alerts[] and total_alerts
```

### Supplier Resolution Flow

```mermaid
flowchart TD
    A["Low-stock candidate for company + product"] --> B["Load company-specific supplier mappings"]
    B --> C{"Preferred mapping exists?"}
    C -->|Yes| D["Return preferred supplier"]
    C -->|No| E{"Exactly one active mapping exists?"}
    E -->|Yes| F["Return sole active supplier"]
    E -->|No active mappings| G["Return supplier = null (missing)"]
    E -->|Multiple active mappings| H["Return supplier = null (ambiguous)"]
```

### Part 1 Ownership Validation Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Create Product API
    participant Auth as Auth Context
    participant DB as Database

    Client->>API: POST /api/products
    API->>Auth: Resolve current company
    API->>DB: Validate SKU uniqueness
    API->>DB: Validate warehouse exists
    API->>DB: Validate warehouse.company_id == current_company.id
    API->>DB: Create product + optional inventory in one transaction
    API->>Client: 201 or structured error
```

### Evaluation Logic Map

```mermaid
flowchart TD
    A["Company exists?"] -->|No| B["404 company_not_found"]
    A -->|Yes| C["Load warehouses"]
    C --> D["Read recent sales within 30 days"]
    D --> E["Group sales by product + warehouse"]
    E --> F["Join inventory rows"]
    F --> G["Resolve threshold from product override or product type"]
    G --> H{"Stock <= threshold?"}
    H -->|No| I["Skip"]
    H -->|Yes| J["Resolve company-scoped supplier"]
    J --> K["Attach supplier or null and stockout estimate"]
    K --> L["Return sorted alerts"]
```
