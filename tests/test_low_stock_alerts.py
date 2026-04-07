from __future__ import annotations


def test_low_stock_alerts_returns_expected_shape_and_order(client):
    response = client.get("/api/companies/1/alerts/low-stock")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total_alerts"] == 3

    alerts = payload["alerts"]
    assert [alert["product_id"] for alert in alerts] == [103, 101, 101]
    assert alerts[0]["warehouse_name"] == "Main Warehouse"
    assert alerts[1]["supplier"]["name"] == "Supplier Corp"
    assert alerts[1]["days_until_stockout"] == 6
    assert alerts[2]["warehouse_name"] == "Overflow Warehouse"
    assert alerts[2]["days_until_stockout"] == 60


def test_recent_sales_filter_excludes_stale_product(client):
    response = client.get("/api/companies/1/alerts/low-stock")

    payload = response.get_json()
    product_ids = {alert["product_id"] for alert in payload["alerts"]}
    assert 102 not in product_ids


def test_contract_fields_match_pdf_response_shape(client):
    response = client.get("/api/companies/1/alerts/low-stock")

    payload = response.get_json()
    first_alert = payload["alerts"][0]
    assert set(first_alert) == {
        "product_id",
        "product_name",
        "sku",
        "warehouse_id",
        "warehouse_name",
        "current_stock",
        "threshold",
        "days_until_stockout",
        "supplier",
    }
