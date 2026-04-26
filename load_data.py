"""
Create retail.db and optionally sample_sales.csv from a fixed synthetic retail dataset.
Run from project root: python load_data.py
"""
import csv
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "retail.db"
CSV_PATH = PROJECT_ROOT / "sample_sales.csv"

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Apparel", "Food"]
PRODUCTS = {
    "Electronics": ["USB Hub", "Battery Pack", "LED Lamp"],
    "Apparel": ["T-Shirt", "Jacket", "Hat"],
    "Food": ["Snack Bar", "Coffee", "Tea"],
}


def build_rows():
    rows_out = []
    oid = 1000
    for month in range(1, 4):
        for day in (5, 15, 25):
            order_date = f"2024-{month:02d}-{day:02d}"
            for region in REGIONS:
                for cat in CATEGORIES:
                    for pname in PRODUCTS[cat][:2]:
                        qty = 1 + (oid % 4)
                        unit = round(10.0 + (oid % 50), 2)
                        total = round(qty * unit, 2)
                        rows_out.append(
                            {
                                "order_id": f"ORD-{oid}",
                                "order_date": order_date,
                                "region": region,
                                "product_category": cat,
                                "product_name": pname,
                                "quantity": qty,
                                "unit_price": unit,
                                "total_sales": total,
                                "customer_id": f"CUST-{(oid % 200) + 1}",
                            }
                        )
                        oid += 1
    return rows_out


def write_csv(rows):
    fieldnames = [
        "order_id",
        "order_date",
        "region",
        "product_category",
        "product_name",
        "quantity",
        "unit_price",
        "total_sales",
        "customer_id",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def load_sqlite(rows):
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE sales (
                order_id TEXT,
                order_date TEXT,
                region TEXT,
                product_category TEXT,
                product_name TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_sales REAL,
                customer_id TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO sales (
                order_id, order_date, region, product_category, product_name,
                quantity, unit_price, total_sales, customer_id
            ) VALUES (
                :order_id, :order_date, :region, :product_category, :product_name,
                :quantity, :unit_price, :total_sales, :customer_id
            )
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def main():
    rows = build_rows()
    write_csv(rows)
    load_sqlite(rows)
    print(f"Wrote {len(rows)} rows to {DB_PATH} and {CSV_PATH}")


if __name__ == "__main__":
    main()
