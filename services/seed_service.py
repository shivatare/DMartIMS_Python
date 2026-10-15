import random
from datetime import datetime
from models import db, Product, SalesHistory


def seed_data():
    if Product.query.count() > 0:
        return

    products = [
        Product(name="Tata Salt 1kg",           category="Grocery",       price=22,   stock_quantity=340, min_stock_level=50,  lead_time_days=3, unit="pkt",  supplier_name="Tata Consumer"),
        Product(name="Aashirvaad Atta 5kg",      category="Grocery",       price=218,  stock_quantity=18,  min_stock_level=30,  lead_time_days=4, unit="bag",  supplier_name="ITC Ltd"),
        Product(name="Amul Butter 500g",         category="Dairy",         price=260,  stock_quantity=95,  min_stock_level=40,  lead_time_days=2, unit="pkt",  supplier_name="Amul"),
        Product(name="Fortune Sunflower Oil 5L", category="Edible Oil",    price=645,  stock_quantity=8,   min_stock_level=20,  lead_time_days=5, unit="btl",  supplier_name="Adani Wilmar"),
        Product(name="Surf Excel 2kg",           category="Home Care",     price=340,  stock_quantity=145, min_stock_level=30,  lead_time_days=3, unit="pkt",  supplier_name="HUL"),
        Product(name="Parle-G 800g",             category="Snacks",        price=80,   stock_quantity=230, min_stock_level=60,  lead_time_days=2, unit="pkt",  supplier_name="Parle Products"),
        Product(name="Maggi Noodles 12pk",       category="Instant Food",  price=144,  stock_quantity=12,  min_stock_level=40,  lead_time_days=3, unit="box",  supplier_name="Nestle India"),
        Product(name="Colgate MaxFresh 150g",    category="Personal Care", price=95,   stock_quantity=180, min_stock_level=50,  lead_time_days=4, unit="tube", supplier_name="Colgate-Palmolive"),
        Product(name="Lays Classic 26g 30pk",    category="Snacks",        price=390,  stock_quantity=76,  min_stock_level=25,  lead_time_days=2, unit="box",  supplier_name="PepsiCo India"),
        Product(name="Basmati Rice 5kg",         category="Grocery",       price=390,  stock_quantity=55,  min_stock_level=30,  lead_time_days=5, unit="bag",  supplier_name="India Gate"),
        Product(name="Horlicks 1kg",             category="Beverages",     price=395,  stock_quantity=42,  min_stock_level=20,  lead_time_days=4, unit="jar",  supplier_name="HUL"),
        Product(name="Dove Soap 100g 4pk",       category="Personal Care", price=196,  stock_quantity=110, min_stock_level=35,  lead_time_days=3, unit="pack", supplier_name="HUL"),
    ]
    db.session.add_all(products)
    db.session.flush()

    base_demand = [45, 22, 18, 12, 15, 38, 25, 20, 14, 18, 10, 22]
    seasonal    = [0.9, 0.85, 0.8, 0.95, 1.0, 1.0, 1.1, 1.3, 1.4, 1.2, 1.15, 1.25]
    months_seq  = [4,5,6,7,8,9,10,11,12,1,2,3]
    years_seq   = [2024]*9 + [2025]*3

    rng = random.Random(42)
    histories = []
    for pi, product in enumerate(products):
        for m in range(12):
            units = int(base_demand[pi] * 30 * seasonal[m] * (0.88 + rng.random() * 0.24))
            histories.append(SalesHistory(
                product_id=product.id,
                year=years_seq[m],
                month=months_seq[m],
                units_sold=units
            ))

    db.session.add_all(histories)
    db.session.commit()
