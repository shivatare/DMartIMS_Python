from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import db, Product

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

CATEGORIES = ["Grocery", "Dairy", "Edible Oil", "Home Care", "Snacks",
              "Instant Food", "Personal Care", "Beverages", "Others"]
UNITS = ["pkt", "bag", "btl", "box", "tube", "jar", "pack", "kg", "L", "dozen"]


@inventory_bp.route("/")
def index():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "All")

    query = Product.query
    if search:
        query = query.filter(
            db.or_(Product.name.contains(search), Product.category.contains(search))
        )
    if category and category != "All":
        query = query.filter_by(category=category)

    products = query.order_by(Product.category, Product.name).all()
    all_categories = [r[0] for r in db.session.query(Product.category).distinct().order_by(Product.category)]

    return render_template("inventory/index.html",
                           products=products, search=search,
                           category=category, categories=all_categories,
                           categories_list=CATEGORIES, units_list=UNITS)


@inventory_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        p = Product(
            name=request.form["name"],
            category=request.form["category"],
            price=float(request.form["price"]),
            stock_quantity=int(request.form["stock_quantity"]),
            min_stock_level=int(request.form["min_stock_level"]),
            lead_time_days=int(request.form["lead_time_days"]),
            unit=request.form.get("unit", "pkt"),
            supplier_name=request.form.get("supplier_name") or None,
            created_at=datetime.now(),
        )
        db.session.add(p)
        db.session.commit()
        flash(f"Product '{p.name}' added successfully.", "success")
        return redirect(url_for("inventory.index"))
    return render_template("inventory/create.html", categories_list=CATEGORIES, units_list=UNITS)


@inventory_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        product.name = request.form["name"]
        product.category = request.form["category"]
        product.price = float(request.form["price"])
        product.stock_quantity = int(request.form["stock_quantity"])
        product.min_stock_level = int(request.form["min_stock_level"])
        product.lead_time_days = int(request.form["lead_time_days"])
        product.unit = request.form.get("unit", "pkt")
        product.supplier_name = request.form.get("supplier_name") or None
        db.session.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for("inventory.index"))
    return render_template("inventory/edit.html", product=product,
                           categories_list=CATEGORIES, units_list=UNITS)


@inventory_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("inventory.index"))


@inventory_bp.route("/restock", methods=["POST"])
def restock():
    product_id = int(request.form["id"])
    quantity = int(request.form["quantity"])
    product = Product.query.get_or_404(product_id)
    product.stock_quantity += quantity
    db.session.commit()
    flash(f"Restocked {quantity} units of {product.name}.", "success")
    return redirect(url_for("inventory.index"))
