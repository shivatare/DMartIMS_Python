from collections import defaultdict

from flask import Blueprint, render_template

from models import db, Product, Sale
from services.forecast_service import get_forecast

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
def index():
    sales = Sale.query.join(Sale.product).all()
    products = Product.query.all()

    cat_map = defaultdict(lambda: {"revenue": 0.0, "units_sold": 0})
    for s in sales:
        cat_map[s.product.category]["revenue"] += s.total_amount
        cat_map[s.product.category]["units_sold"] += s.quantity
    category_revenue = sorted(
        [{"category": k, **v} for k, v in cat_map.items()],
        key=lambda x: -x["revenue"],
    )

    forecast_map = {}
    for p in products:
        f = get_forecast(p.id, 1)
        forecast_map[p.id] = f["forecasts"][0]["predicted_units"] if f["forecasts"] else 0.0

    # Inventory value by category for doughnut chart
    inv_cat = defaultdict(float)
    for p in products:
        inv_cat[p.category] += p.stock_value
    inv_by_cat = sorted([{"category": k, "value": v} for k, v in inv_cat.items()],
                        key=lambda x: -x["value"])

    recent_sales = sorted(sales, key=lambda s: s.sale_date, reverse=True)[:20]

    vm = {
        "total_revenue": sum(s.total_amount for s in sales),
        "total_transactions": len(sales),
        "total_inventory_value": sum(p.stock_value for p in products),
        "recent_sales": recent_sales,
        "category_revenue": category_revenue,
        "all_products": products,
        "forecast_map": forecast_map,
        "inv_by_cat": inv_by_cat,
    }
    return render_template("reports/index.html", **vm)
