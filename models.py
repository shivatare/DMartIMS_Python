from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    min_stock_level = db.Column(db.Integer, nullable=False, default=10)
    lead_time_days = db.Column(db.Integer, nullable=False, default=3)
    unit = db.Column(db.String(20), default="pkt")
    supplier_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    sales = db.relationship("Sale", back_populates="product", lazy="dynamic")
    sales_histories = db.relationship("SalesHistory", back_populates="product", lazy="dynamic")

    @property
    def stock_status(self):
        if self.stock_quantity <= self.min_stock_level * 0.4:
            return "Critical"
        elif self.stock_quantity <= self.min_stock_level:
            return "Low"
        return "OK"

    @property
    def stock_value(self):
        return float(self.price) * self.stock_quantity


class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.now)
    notes = db.Column(db.String(100), nullable=True)

    product = db.relationship("Product", back_populates="sales")

    @property
    def total_amount(self):
        return float(self.unit_price) * self.quantity


class SalesHistory(db.Model):
    __tablename__ = "sales_histories"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", back_populates="sales_histories")

    @property
    def month_label(self):
        return datetime(self.year, self.month, 1).strftime("%b %y")
