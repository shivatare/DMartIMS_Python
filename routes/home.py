from datetime import datetime, date
from collections import defaultdict

from flask import Blueprint, render_template

from models import db, Product, Sale, SalesHistory

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    products = Product.query.all()
    today = date.today()
    month_start = today.replace(day=1)

    today_sales = (
        Sale.query
        .join(Sale.product)
        .filter(db.func.date(Sale.sale_date) == today)
        .all()
    )
    month_sales = (
        Sale.query
        .join(Sale.product)
        .filter(Sale.sale_date >= month_start)
        .all()
    )

    # Category stocks
    cat_map = defaultdict(lambda: {"total_stock": 0, "total_value": 0.0})
    for p in products:
        cat_map[p.category]["total_stock"] += p.stock_quantity
        cat_map[p.category]["total_value"] += p.stock_value
    category_stocks = sorted(
        [{"category": k, **v} for k, v in cat_map.items()],
        key=lambda x: -x["total_stock"],
    )

    # History of first product
    first = products[0] if products else None
    top_history = []
    if first:
        top_history = (
            SalesHistory.query
            .filter_by(product_id=first.id)
            .order_by(SalesHistory.year, SalesHistory.month)
            .all()
        )

    low_stock = [p for p in products if p.stock_status != "OK"]
    critical = [p for p in products if p.stock_status == "Critical"]

    vm = {
        "total_products": len(products),
        "low_stock_count": len(low_stock),
        "critical_stock_count": len(critical),
        "total_inventory_value": sum(p.stock_value for p in products),
        "today_sales_value": sum(s.total_amount for s in today_sales),
        "today_transactions": len(today_sales),
        "month_sales_value": sum(s.total_amount for s in month_sales),
        "low_stock_products": low_stock,
        "category_stocks": category_stocks,
        "top_product_history": top_history,
        "now": datetime.now(),
    }

    return render_template("home/index.html", **vm)
