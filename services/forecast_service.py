import math
from datetime import datetime

import numpy as np

from models import Product, SalesHistory


def get_forecast(product_id: int, horizon_months: int = 3) -> dict:
    """
    Produce a demand forecast using Holt-Winters Exponential Smoothing
    (equivalent role to ML.NET SSA in the original C# project).
    Returns a dict matching ForecastResult shape.
    """
    product = Product.query.get(product_id)
    if not product:
        return _empty_result(product_id, "", horizon_months)

    history = (
        SalesHistory.query
        .filter_by(product_id=product_id)
        .order_by(SalesHistory.year, SalesHistory.month)
        .all()
    )

    future_months = [
        datetime.now().replace(day=1).__class__(
            datetime.now().year + (datetime.now().month + i - 1) // 12,
            (datetime.now().month + i - 1) % 12 + 1,
            1,
        ).strftime("%b %y")
        for i in range(1, horizon_months + 1)
    ]

    if len(history) < 4:
        return {
            "product_id": product_id,
            "product_name": product.name,
            "mae": 0.0, "rmse": 0.0, "mape": 0.0,
            "reorder_point": product.min_stock_level,
            "suggested_order_qty": 0,
            "forecasts": [
                {"month": m, "predicted_units": 100.0, "lower_bound": 80.0, "upper_bound": 120.0}
                for m in future_months
            ],
        }

    values = np.array([h.units_sold for h in history], dtype=float)

    # Forecast using simple Holt-Winters / exponential smoothing
    predicted, lower, upper = _ssa_like_forecast(values, horizon_months)

    # Compute MAE/RMSE/MAPE on last-3 hold-out if enough data
    mae = rmse = mape = 0.0
    if len(history) >= 6:
        train = values[:-3]
        actual = values[-3:]
        test_pred, _, _ = _ssa_like_forecast(train, 3)
        n = min(len(actual), len(test_pred))
        errors = np.abs(actual[:n] - test_pred[:n])
        mae = float(np.mean(errors))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        with np.errstate(divide="ignore", invalid="ignore"):
            mape_arr = np.where(actual[:n] > 0, errors / actual[:n], 0)
        mape = float(np.mean(mape_arr) * 100)

    # Reorder point
    recent = values[-3:] if len(values) >= 3 else values
    avg_daily = float(np.mean(recent)) / 30.0
    safety_stock = avg_daily * product.lead_time_days * 0.5
    reorder_point = int(avg_daily * product.lead_time_days + safety_stock)
    suggested_qty = max(0, int(predicted[0]) + reorder_point - product.stock_quantity)

    forecasts = []
    for i, month in enumerate(future_months):
        forecasts.append({
            "month": month,
            "predicted_units": max(0.0, float(predicted[i])) if i < len(predicted) else 0.0,
            "lower_bound": max(0.0, float(lower[i])) if i < len(lower) else 0.0,
            "upper_bound": float(upper[i]) if i < len(upper) else 0.0,
        })

    return {
        "product_id": product_id,
        "product_name": product.name,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "reorder_point": reorder_point,
        "suggested_order_qty": suggested_qty,
        "forecasts": forecasts,
    }


def _ssa_like_forecast(values: np.ndarray, horizon: int):
    """
    Holt-Winters additive forecast with 95% confidence bounds.
    Falls back to simple exponential smoothing for short series.
    """
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        if len(values) >= 8:
            model = ExponentialSmoothing(
                values, trend="add", seasonal="add", seasonal_periods=min(4, len(values) // 2)
            ).fit(optimized=True, use_brute=False)
        else:
            model = ExponentialSmoothing(values, trend="add").fit(optimized=True)

        forecast_vals = model.forecast(horizon)
        residuals = values - model.fittedvalues
        std_err = float(np.std(residuals)) if len(residuals) > 1 else float(np.std(values) * 0.2)

        z = 1.96  # 95% CI
        lower = forecast_vals - z * std_err
        upper = forecast_vals + z * std_err
        return forecast_vals, lower, upper

    except Exception:
        # Fallback: moving average
        window = min(3, len(values))
        avg = float(np.mean(values[-window:]))
        std = float(np.std(values[-window:])) if window > 1 else avg * 0.2
        pred = np.full(horizon, avg)
        return pred, pred - 1.96 * std, pred + 1.96 * std


def _empty_result(product_id, name, horizon):
    future_months = [
        datetime.now().replace(day=1).__class__(
            datetime.now().year + (datetime.now().month + i - 1) // 12,
            (datetime.now().month + i - 1) % 12 + 1,
            1,
        ).strftime("%b %y")
        for i in range(1, horizon + 1)
    ]
    return {
        "product_id": product_id,
        "product_name": name,
        "mae": 0.0, "rmse": 0.0, "mape": 0.0,
        "reorder_point": 0,
        "suggested_order_qty": 0,
        "forecasts": [
            {"month": m, "predicted_units": 0.0, "lower_bound": 0.0, "upper_bound": 0.0}
            for m in future_months
        ],
    }
