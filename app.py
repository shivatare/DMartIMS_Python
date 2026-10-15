import os
from flask import Flask
from models import db
from routes.home import home_bp
from routes.inventory import inventory_bp
from routes.sales import sales_bp
from routes.alerts import alerts_bp
from routes.forecast import forecast_bp
from routes.reports import reports_bp


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dmart.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dmart-ims-secret-key-2024"

    db.init_app(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(forecast_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()
        from services.seed_service import seed_data
        seed_data()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
