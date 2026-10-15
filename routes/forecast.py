from flask import Blueprint, render_template, request, jsonify

from models import Product, SalesHistory
from services.forecast_service import get_forecast

forecast_bp = Blueprint("forecast", __name__, url_prefix="/forecast")


@forecast_bp.route("/")
def index():
    products = Product.query.order_by(Product.name).all()
    product_id = request.args.get("product_id", type=int)
    selected_id = product_id or (products[0].id if products else 1)

    forecast = get_forecast(selected_id, 3)
    history = (
        SalesHistory.query
        .filter_by(product_id=selected_id)
        .order_by(SalesHistory.year, SalesHistory.month)
        .all()
    )
    selected = next((p for p in products if p.id == selected_id), None)

    avg_monthly = (sum(h.units_sold for h in history[-3:]) / min(3, len(history[-3:]))) if history else 0
    avg_daily = avg_monthly / 30.0
    safety = avg_daily * (selected.lead_time_days if selected else 3) * 0.5

    return render_template("forecast/index.html",
                           products=products,
                           selected_id=selected_id,
                           selected=selected,
                           forecast=forecast,
                           history=history,
                           avg_daily=avg_daily,
                           safety=safety)


@forecast_bp.route("/get_forecast_data")
def get_forecast_data():
    product_id = request.args.get("product_id", type=int)
    forecast = get_forecast(product_id, 3)
    history = (
        SalesHistory.query
        .filter_by(product_id=product_id)
        .order_by(SalesHistory.year, SalesHistory.month)
        .all()
    )
    hist_data = [{"month": h.month, "year": h.year, "units_sold": h.units_sold} for h in history]
    return jsonify({"forecast": forecast, "history": hist_data})
