from __future__ import annotations


def test_unknown_company_returns_404(client):
    response = client.get("/api/companies/999/alerts/low-stock")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["error"]["code"] == "company_not_found"


def test_ambiguous_supplier_mapping_returns_null_supplier(client):
    response = client.get("/api/companies/1/alerts/low-stock")

    payload = response.get_json()
    bundle_alert = next(alert for alert in payload["alerts"] if alert["product_id"] == 103)
    assert bundle_alert["supplier"] is None


def test_missing_threshold_configuration_excludes_product(client):
    response = client.get("/api/companies/1/alerts/low-stock")

    payload = response.get_json()
    product_ids = {alert["product_id"] for alert in payload["alerts"]}
    assert 104 not in product_ids


def test_preferred_supplier_is_returned_for_widget_a(client):
    response = client.get("/api/companies/1/alerts/low-stock")

    payload = response.get_json()
    widget_alert = next(alert for alert in payload["alerts"] if alert["product_id"] == 101)
    assert widget_alert["supplier"]["name"] == "Supplier Corp"
