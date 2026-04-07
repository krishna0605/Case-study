# Part 3: API Implementation

## 1. Write Implementation

The implementation is in [app.py](C:/Users/ADMIN/Desktop/Bynry%20-%20Case%20study%20submission/Part%203/app.py).

Endpoint:

`GET /api/companies/{company_id}/alerts/low-stock`

## 2. Handle Edge Cases

1. Unknown company returns `404`.
2. Company with no warehouses returns an empty alert list.
3. Products without recent sales are excluded.
4. Products above threshold are excluded.
5. Products without threshold configuration are excluded.
6. Missing supplier mapping returns `supplier: null`.
7. Ambiguous supplier mapping also returns `supplier: null` instead of guessing.
8. Multiple warehouses for the same company are handled independently.

## 3. Explain Approach

- The endpoint validates the company first, then loads the company's warehouses.
- Recent sales are filtered to a 30-day window and grouped by product and warehouse.
- Threshold is resolved from product override first, then product type.
- Only products with recent sales and stock at or below threshold are returned.
- Supplier resolution is company-specific and deterministic.
- The response is sorted to keep output stable across runs.

## Assumptions

- Recent sales means sales within the last 30 days.
- Alerts are evaluated per product per warehouse.
- `days_until_stockout = floor(current_stock / average_daily_sales)` when average daily sales is greater than zero.
- If supplier mapping is missing or ambiguous, the API returns `supplier: null`.
- Products without threshold configuration are excluded until catalog setup is complete.
