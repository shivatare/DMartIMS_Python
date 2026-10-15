from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from models import db, Product, Sale

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


@sales_bp.route("/")
def index():
    products = Product.query.order_by(Product.name).all()
    today = date.today().strftime("%Y-%m-%d")
    return render_template("sales/index.html", products=products, today=today)


@sales_bp.route("/create", methods=["POST"])
def create():
    product_id = int(request.form["product_id"])
    quantity = int(request.form.get("quantity", 0))
    sale_date_str = request.form.get("sale_date", "")
    notes = request.form.get("notes", "").strip() or None

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("sales.index"))

    if quantity <= 0 or quantity > product.stock_quantity:
        flash(f"Invalid quantity. Available stock: {product.stock_quantity} {product.unit}.", "error")
        return redirect(url_for("sales.index"))

    try:
        sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d")
    except ValueError:
        sale_date = datetime.now()

    sale = Sale(
        product_id=product_id,
        quantity=quantity,
        unit_price=product.price,
        sale_date=sale_date,
        notes=notes,
    )
    product.stock_quantity -= quantity
    db.session.add(sale)
    db.session.commit()

    total = float(product.price) * quantity
    flash(f"Sale recorded: {quantity} × {product.name} = ₹{total:,.2f}", "success")
    return redirect(url_for("sales.index"))


@sales_bp.route("/history")
def history():
    sales = (
        Sale.query
        .join(Sale.product)
        .order_by(Sale.sale_date.desc())
        .limit(100)
        .all()
    )
    return render_template("sales/history.html", sales=sales)


@sales_bp.route("/get_product/<int:id>")
def get_product(id):
    p = Product.query.get_or_404(id)
    return jsonify({"price": float(p.price), "stock_quantity": p.stock_quantity,
                    "unit": p.unit, "name": p.name})
