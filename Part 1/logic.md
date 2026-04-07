# Part 1: Code Review & Debugging

## 1. Identify Issues

1. The handler trusts `request.json` and does not validate malformed or missing input.
2. Direct key access like `data['name']` can raise runtime errors when fields are missing.
3. The code stores `warehouse_id` on the product even though products can exist in multiple warehouses.
4. SKU uniqueness is not enforced before insert.
5. `price` is not parsed safely as a decimal.
6. `initial_quantity` is not validated for type or non-negative value.
7. `warehouse_id` is not validated for existence.
8. Warehouse ownership is not validated, so cross-company writes are possible.
9. Product creation and inventory creation use two separate commits.
10. A failure after the first commit leaves partial data behind.
11. The code can create duplicate inventory rows for the same product and warehouse.
12. Optional fields are not handled even though the prompt says some fields might be optional.
13. The endpoint does not return explicit HTTP status codes for success, validation errors, or conflicts.
14. Error responses are not structured for clients.

## 2. Explain Impact

1. Bad input can cause `500` errors instead of client-readable validation failures.
2. Storing `warehouse_id` on the product breaks the multi-warehouse requirement.
3. Duplicate SKUs can corrupt catalog identity and downstream lookups.
4. Unsafe numeric handling can produce incorrect price values.
5. Negative or invalid inventory values create impossible stock states.
6. Inventory can be written against a non-existent warehouse.
7. Inventory can be attached to another company's warehouse, which is a tenant-isolation issue.
8. Two commits can leave a product created without its intended inventory record.
9. Duplicate inventory rows make current stock ambiguous.
10. API consumers cannot reliably distinguish success, invalid requests, and conflicts.

## 3. Provide Fixes

The corrected implementation is in [code.py](C:/Users/ADMIN/Desktop/Bynry%20-%20Case%20study%20submission/Part%201/code.py).

### Explanation

- The main modeling fix is separating product catalog data from warehouse inventory state.
- The endpoint validates required fields, decimal price input, optional quantity rules, and non-negative stock.
- Product creation and optional inventory creation are handled in one transaction.
- Warehouse checks validate both existence and ownership.
- The response uses stable error objects and appropriate status codes like `201`, `400`, `403`, `404`, and `409`.
