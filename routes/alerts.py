from flask import Blueprint, render_template

from models import Product
from services.forecast_service import get_forecast

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts_bp.route("/")
def index():
    products = Product.query.all()
    low_stock = [p for p in products if p.stock_status != "OK"]
    critical = [p for p in products if p.stock_status == "Critical"]
    low_only = [p for p in low_stock if p.stock_status == "Low"]

    reorder_map = {}
    for p in products:
        f = get_forecast(p.id, 1)
        reorder_map[p.id] = f["reorder_point"]

    # Sort: critical first, then low, then ok
    sort_key = lambda p: 0 if p.stock_status == "Critical" else 1 if p.stock_status == "Low" else 2
    all_sorted = sorted(products, key=sort_key)

    return render_template("alerts/index.html",
                           all_products=all_sorted,
                           low_stock=low_stock,
                           critical=critical,
                           low_only=low_only,
                           reorder_map=reorder_map)
