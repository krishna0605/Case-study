from decimal import Decimal, InvalidOperation

from flask import request
from sqlalchemy.exc import IntegrityError


@app.route("/api/products", methods=["POST"])
def create_product():
    payload = request.get_json(silent=True) or {}
    current_company = get_current_company()

    required_fields = ["name", "sku", "price"]
    missing_fields = [field for field in required_fields if not payload.get(field)]
    if missing_fields:
        return {
            "error": {
                "code": "validation_error",
                "message": f"Missing required fields: {', '.join(missing_fields)}",
            }
        }, 400

    try:
        price = Decimal(str(payload["price"]))
    except (InvalidOperation, TypeError, ValueError):
        return {
            "error": {
                "code": "validation_error",
                "message": "price must be a valid decimal value",
            }
        }, 400

    initial_quantity = payload.get("initial_quantity")
    warehouse_id = payload.get("warehouse_id")

    if initial_quantity is not None:
        if warehouse_id is None:
            return {
                "error": {
                    "code": "validation_error",
                    "message": "warehouse_id is required when initial_quantity is provided",
                }
            }, 400
        if not isinstance(initial_quantity, int) or initial_quantity < 0:
            return {
                "error": {
                    "code": "validation_error",
                    "message": "initial_quantity must be a non-negative integer",
                }
            }, 400

    existing_product = Product.query.filter_by(sku=payload["sku"].strip()).first()
    if existing_product:
        return {
            "error": {
                "code": "sku_conflict",
                "message": f"SKU {payload['sku']} already exists",
            }
        }, 409

    try:
        product = Product(
            name=payload["name"].strip(),
            sku=payload["sku"].strip(),
            price=price,
        )
        db.session.add(product)
        db.session.flush()

        # Product is catalog-level. Inventory is warehouse-level.
        if warehouse_id is not None and initial_quantity is not None:
            warehouse = Warehouse.query.get(warehouse_id)
            if warehouse is None:
                db.session.rollback()
                return {
                    "error": {
                        "code": "warehouse_not_found",
                        "message": f"Warehouse {warehouse_id} does not exist",
                    }
                }, 404

            if warehouse.company_id != current_company.id:
                db.session.rollback()
                return {
                    "error": {
                        "code": "warehouse_forbidden",
                        "message": (
                            f"Warehouse {warehouse_id} does not belong to "
                            f"company {current_company.id}"
                        ),
                    }
                }, 403

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=warehouse_id,
                quantity=initial_quantity,
            )
            db.session.add(inventory)

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {
            "error": {
                "code": "conflict",
                "message": "Unable to create product because of a data integrity conflict",
            }
        }, 409
    except Exception:
        db.session.rollback()
        return {
            "error": {
                "code": "unexpected_error",
                "message": "Unexpected failure while creating product",
            }
        }, 500

    return {"message": "Product created", "product_id": product.id}, 201
