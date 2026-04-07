from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from flask import Flask, jsonify


# Assumptions documented per the prompt:
# 1. "Recent sales activity" means sales within the last 30 days.
# 2. Alerts are evaluated per product per warehouse.
# 3. If a product override threshold exists, it takes precedence over the product type threshold.
# 4. If supplier mapping is missing or ambiguous, the API returns supplier = null.
# 5. Products without threshold configuration are excluded until catalog setup is complete.


@dataclass(frozen=True)
class Company:
    id: int
    name: str


@dataclass(frozen=True)
class Warehouse:
    id: int
    company_id: int
    name: str


@dataclass(frozen=True)
class ProductType:
    id: int
    name: str
    low_stock_threshold: Optional[int]


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    sku: str
    price: Decimal
    product_type_id: int
    override_low_stock_threshold: Optional[int] = None


@dataclass(frozen=True)
class InventoryLevel:
    product_id: int
    warehouse_id: int
    quantity: int


@dataclass(frozen=True)
class Supplier:
    id: int
    name: str
    contact_email: str


@dataclass(frozen=True)
class CompanySupplier:
    company_id: int
    supplier_id: int
    is_active: bool = True


@dataclass(frozen=True)
class CompanySupplierProduct:
    company_id: int
    product_id: int
    supplier_id: int
    is_preferred: bool = False


@dataclass(frozen=True)
class SalesOrderItem:
    id: int
    product_id: int
    warehouse_id: int
    quantity: int
    sold_at: datetime


class DemoRepository:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.companies = [
            Company(id=1, name="Acme Retail"),
            Company(id=2, name="Northwind Foods"),
        ]
        self.warehouses = [
            Warehouse(id=1, company_id=1, name="Main Warehouse"),
            Warehouse(id=2, company_id=1, name="Overflow Warehouse"),
            Warehouse(id=3, company_id=2, name="Remote Depot"),
        ]
        self.product_types = [
            ProductType(id=1, name="Fast Moving", low_stock_threshold=20),
            ProductType(id=2, name="Slow Moving", low_stock_threshold=8),
            ProductType(id=3, name="Unconfigured", low_stock_threshold=None),
        ]
        self.products = [
            Product(id=101, name="Widget A", sku="WID-001", price=Decimal("49.99"), product_type_id=1),
            Product(
                id=102,
                name="Widget B",
                sku="WID-002",
                price=Decimal("29.99"),
                product_type_id=2,
                override_low_stock_threshold=14,
            ),
            Product(id=103, name="Bundle Kit", sku="KIT-100", price=Decimal("79.99"), product_type_id=1),
            Product(id=104, name="Mystery Part", sku="MYS-404", price=Decimal("19.99"), product_type_id=3),
        ]
        self.inventory_levels = [
            InventoryLevel(product_id=101, warehouse_id=1, quantity=5),
            InventoryLevel(product_id=101, warehouse_id=2, quantity=18),
            InventoryLevel(product_id=102, warehouse_id=1, quantity=12),
            InventoryLevel(product_id=103, warehouse_id=1, quantity=0),
            InventoryLevel(product_id=104, warehouse_id=1, quantity=3),
            InventoryLevel(product_id=101, warehouse_id=3, quantity=4),
        ]
        self.suppliers = [
            Supplier(id=201, name="Supplier Corp", contact_email="orders@supplier.com"),
            Supplier(id=202, name="Backup Supply", contact_email="sales@backup.example"),
            Supplier(id=203, name="Global Industrial", contact_email="ops@global.example"),
        ]
        self.company_suppliers = [
            CompanySupplier(company_id=1, supplier_id=201, is_active=True),
            CompanySupplier(company_id=1, supplier_id=202, is_active=True),
            CompanySupplier(company_id=1, supplier_id=203, is_active=True),
            CompanySupplier(company_id=2, supplier_id=202, is_active=True),
        ]
        self.company_supplier_products = [
            CompanySupplierProduct(company_id=1, product_id=101, supplier_id=201, is_preferred=True),
            CompanySupplierProduct(company_id=2, product_id=101, supplier_id=202, is_preferred=True),
            CompanySupplierProduct(company_id=1, product_id=103, supplier_id=202, is_preferred=False),
            CompanySupplierProduct(company_id=1, product_id=103, supplier_id=203, is_preferred=False),
        ]
        self.sales_order_items = [
            SalesOrderItem(id=1, product_id=101, warehouse_id=1, quantity=15, sold_at=now - timedelta(days=3)),
            SalesOrderItem(id=2, product_id=101, warehouse_id=1, quantity=10, sold_at=now - timedelta(days=10)),
            SalesOrderItem(id=3, product_id=101, warehouse_id=2, quantity=9, sold_at=now - timedelta(days=5)),
            SalesOrderItem(id=4, product_id=102, warehouse_id=1, quantity=5, sold_at=now - timedelta(days=45)),
            SalesOrderItem(id=5, product_id=103, warehouse_id=1, quantity=4, sold_at=now - timedelta(days=8)),
            SalesOrderItem(id=6, product_id=104, warehouse_id=1, quantity=7, sold_at=now - timedelta(days=7)),
        ]

    def get_company(self, company_id: int) -> Company | None:
        return next((company for company in self.companies if company.id == company_id), None)

    def get_company_warehouses(self, company_id: int) -> list[Warehouse]:
        return [warehouse for warehouse in self.warehouses if warehouse.company_id == company_id]

    def get_product(self, product_id: int) -> Product | None:
        return next((product for product in self.products if product.id == product_id), None)

    def get_product_type(self, product_type_id: int) -> ProductType | None:
        return next((product_type for product_type in self.product_types if product_type.id == product_type_id), None)

    def get_inventory_for_warehouse_ids(self, warehouse_ids: set[int]) -> list[InventoryLevel]:
        return [inventory for inventory in self.inventory_levels if inventory.warehouse_id in warehouse_ids]

    def get_recent_sales(self, warehouse_ids: set[int], cutoff: datetime) -> list[SalesOrderItem]:
        return [
            sale
            for sale in self.sales_order_items
            if sale.warehouse_id in warehouse_ids and sale.sold_at >= cutoff
        ]

    def resolve_supplier_for_company_product(self, company_id: int, product_id: int) -> Optional[Supplier]:
        active_supplier_ids = {
            link.supplier_id
            for link in self.company_suppliers
            if link.company_id == company_id and link.is_active
        }
        mappings = [
            mapping
            for mapping in self.company_supplier_products
            if mapping.company_id == company_id
            and mapping.product_id == product_id
            and mapping.supplier_id in active_supplier_ids
        ]
        preferred = [mapping for mapping in mappings if mapping.is_preferred]
        if len(preferred) == 1:
            return next((supplier for supplier in self.suppliers if supplier.id == preferred[0].supplier_id), None)
        if len(mappings) == 1:
            return next((supplier for supplier in self.suppliers if supplier.id == mappings[0].supplier_id), None)
        return None


def create_app() -> Flask:
    app = Flask(__name__)
    repository = DemoRepository()
    recent_sales_days = 30

    @app.get("/api/companies/<int:company_id>/alerts/low-stock")
    def get_low_stock_alerts(company_id: int):
        company = repository.get_company(company_id)
        if company is None:
            return jsonify({"error": {"code": "company_not_found", "message": f"Company {company_id} was not found."}}), 404

        warehouses = repository.get_company_warehouses(company_id)
        if not warehouses:
            return jsonify({"alerts": [], "total_alerts": 0}), 200

        warehouse_ids = {warehouse.id for warehouse in warehouses}
        warehouse_lookup = {warehouse.id: warehouse for warehouse in warehouses}
        cutoff = datetime.now(timezone.utc) - timedelta(days=recent_sales_days)
        recent_sales = repository.get_recent_sales(warehouse_ids, cutoff)

        # Only products with recent sales activity are considered for alerts.
        sales_by_key: dict[tuple[int, int], int] = {}
        for sale in recent_sales:
            key = (sale.product_id, sale.warehouse_id)
            sales_by_key[key] = sales_by_key.get(key, 0) + sale.quantity

        if not sales_by_key:
            return jsonify({"alerts": [], "total_alerts": 0}), 200

        alerts = []
        for inventory in repository.get_inventory_for_warehouse_ids(warehouse_ids):
            key = (inventory.product_id, inventory.warehouse_id)
            total_recent_units = sales_by_key.get(key)
            if total_recent_units is None:
                continue

            product = repository.get_product(inventory.product_id)
            if product is None:
                continue

            product_type = repository.get_product_type(product.product_type_id)
            threshold = product.override_low_stock_threshold
            if threshold is None and product_type is not None:
                threshold = product_type.low_stock_threshold

            # Edge case: products without threshold configuration are excluded.
            if threshold is None:
                continue

            if inventory.quantity > threshold:
                continue

            average_daily_sales = total_recent_units / recent_sales_days
            days_until_stockout = None
            if average_daily_sales > 0:
                days_until_stockout = math.floor(inventory.quantity / average_daily_sales)

            supplier = repository.resolve_supplier_for_company_product(company_id, product.id)
            warehouse = warehouse_lookup[inventory.warehouse_id]

            alerts.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku": product.sku,
                    "warehouse_id": warehouse.id,
                    "warehouse_name": warehouse.name,
                    "current_stock": inventory.quantity,
                    "threshold": threshold,
                    "days_until_stockout": days_until_stockout,
                    "supplier": None
                    if supplier is None
                    else {
                        "id": supplier.id,
                        "name": supplier.name,
                        "contact_email": supplier.contact_email,
                    },
                }
            )

        # Stable sorting keeps the response deterministic across runs.
        alerts.sort(key=lambda alert: (alert["current_stock"], alert["product_name"].lower(), alert["warehouse_name"].lower()))
        return jsonify({"alerts": alerts, "total_alerts": len(alerts)}), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
