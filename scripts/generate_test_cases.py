"""Write test_cases.json using counts from retail.db (run after load_data.py)."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "retail.db"


def main():
    conn = sqlite3.connect(DB)
    n_names = conn.execute(
        "SELECT COUNT(DISTINCT product_name) FROM sales"
    ).fetchone()[0]
    months = conn.execute(
        "SELECT COUNT(DISTINCT substr(order_date, 1, 7)) FROM sales"
    ).fetchone()[0]
    conn.close()

    cases = []

    def add(q, frags, rc):
        cases.append(
            {
                "question": q,
                "expected_sql_contains": frags,
                "expected_row_count": rc,
            }
        )

    add("What is the sum of total_sales across all orders?", ["SUM", "total_sales"], 1)
    add("Total revenue from all sales", ["SUM", "total_sales"], 1)
    add("Combine all total_sales into one number", ["SUM", "total_sales"], 1)
    add("How many orders are in the sales table?", ["COUNT", "sales"], 1)
    add("Count every row in sales", ["COUNT"], 1)
    add("What is the average unit_price?", ["AVG", "unit_price"], 1)
    add("Mean unit price", ["AVG", "unit_price"], 1)
    add("Average quantity sold per line", ["AVG", "quantity"], 1)
    add("What is the maximum total_sales?", ["MAX", "total_sales"], 1)
    add("Largest single order total_sales", ["MAX", "total_sales"], 1)
    add("Minimum total_sales amount", ["MIN", "total_sales"], 1)
    add("How many distinct customers appear?", ["COUNT", "customer_id"], 1)
    add("Count distinct customer_id values", ["DISTINCT", "customer_id"], 1)

    add("Show total sales grouped by region", ["region", "GROUP BY", "SUM"], 4)
    add("What were total sales by region?", ["region", "GROUP BY"], 4)
    add("Sales totals for each region", ["region", "SUM"], 4)
    add("Break down revenue by region", ["region", "GROUP BY"], 4)

    add(
        "Total sales for each product_category",
        ["product_category", "GROUP BY", "SUM"],
        3,
    )
    add("Revenue by product category", ["product_category", "SUM"], 3)
    add(
        "Aggregate total_sales by category",
        ["product_category", "GROUP BY"],
        3,
    )

    add(
        "List each product_name with its total sales",
        ["product_name", "SUM"],
        n_names,
    )
    add("Sum quantity grouped by region", ["region", "quantity"], 4)
    add("Top line: sum quantity by region", ["quantity", "region", "SUM"], 4)

    add("What were total sales in January 2024?", ["total_sales", "2024"], 1)
    add("Count orders in January 2024", ["2024-01", "COUNT"], 1)

    add("How many sales records exist?", ["COUNT"], 1)
    add("What are the distinct regions?", ["region"], 4)
    add("List distinct region values", ["DISTINCT", "region"], 4)

    add(
        "Total sales grouped by region and product_category",
        ["region", "product_category", "SUM"],
        12,
    )
    add("Sales by region and category", ["region", "product_category"], 12)

    add("Select all columns from sales limit 10", ["LIMIT", "10"], 10)
    add("Show 5 rows from sales", ["LIMIT", "5"], 5)
    add("First 20 orders by order_date", ["LIMIT", "20"], 20)

    add("How many orders are in the North region?", ["North", "COUNT"], 1)
    add("Count sales rows where region equals North", ["North", "COUNT"], 1)

    add("Total sales in the South region", ["South", "SUM"], 1)
    add(
        "Show total sales by calendar month in 2024",
        ["total_sales", "GROUP BY"],
        months,
    )

    add("Average unit_price by product_category", ["AVG", "product_category"], 3)
    add("Max quantity by region", ["MAX", "region"], 4)
    add("What is the sum of quantity across all rows?", ["SUM", "quantity"], 1)
    add("What is the lowest unit_price?", ["MIN", "unit_price"], 1)
    add("Count distinct product_name", ["DISTINCT", "product_name"], 1)

    add("Aggregate sum of total_sales", ["SUM", "total_sales"], 1)
    add("Report count of orders", ["COUNT"], 1)
    add("Compute average of unit_price", ["AVG", "unit_price"], 1)
    add("Give me max total_sales", ["MAX", "total_sales"], 1)
    add("Smallest unit_price in the dataset", ["MIN", "unit_price"], 1)
    add("Sum quantities for West region", ["West", "SUM", "quantity"], 1)
    add("East region total_sales sum", ["East", "SUM"], 1)
    add(
        "Group sales by region and show sum of total_sales",
        ["GROUP BY", "region"],
        4,
    )
    add(
        "For each product_category show sum total_sales",
        ["product_category", "SUM"],
        3,
    )
    add(
        "Total quantity grouped by product_category",
        ["quantity", "product_category"],
        3,
    )
    add("Average total_sales per order line", ["AVG", "total_sales"], 1)
    add("How many unique order_id values exist?", ["COUNT", "order_id"], 1)
    add("Distinct regions count", ["COUNT", "region"], 1)
    add("List regions with their order counts", ["region", "COUNT"], 4)
    add("Sales in February 2024 total", ["2024-02", "SUM"], 1)
    add("March 2024 revenue sum", ["2024-03", "total_sales"], 1)
    add("Apparel items count", ["Apparel", "COUNT"], 1)
    add("Food category row count", ["Food", "COUNT"], 1)
    add("Count Electronics category rows", ["Electronics", "COUNT"], 1)

    out = ROOT / "test_cases.json"
    out.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {out}")


if __name__ == "__main__":
    main()
