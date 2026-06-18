"""
Retail Data Analysis - Python Script
Generates synthetic retail data and performs comprehensive analysis.
Outputs: JSON data file consumed by the HTML dashboard.
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────────────────
random.seed(42)
OUTPUT_JSON = "retail_data.json"

CATEGORIES = ["Electronics", "Clothing", "Groceries", "Home & Garden", "Sports", "Beauty", "Toys"]
REGIONS     = ["North", "South", "East", "West", "Central"]
PRODUCTS = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Smartwatch", "Camera", "Speaker"],
    "Clothing":    ["T-Shirt", "Jeans", "Jacket", "Dress", "Shoes", "Sweater", "Shorts"],
    "Groceries":   ["Organic Milk", "Bread", "Eggs", "Coffee", "Juice", "Pasta", "Rice"],
    "Home & Garden":["Sofa", "Lamp", "Curtains", "Plant Pot", "Rug", "Mirror", "Shelf"],
    "Sports":      ["Running Shoes", "Yoga Mat", "Dumbbells", "Cycling Helmet", "Tennis Racket", "Football", "Swim Goggles"],
    "Beauty":      ["Moisturizer", "Lipstick", "Shampoo", "Perfume", "Sunscreen", "Foundation", "Nail Polish"],
    "Toys":        ["LEGO Set", "Board Game", "Puzzle", "Action Figure", "Doll", "RC Car", "Craft Kit"],
}
PRICE_RANGE = {
    "Electronics": (150, 1500), "Clothing": (15, 200), "Groceries": (2, 30),
    "Home & Garden": (30, 800), "Sports": (20, 300), "Beauty": (10, 150), "Toys": (10, 120),
}

# ── Data Generation ────────────────────────────────────────────────────────────
def generate_transactions(n=1200):
    transactions = []
    start = datetime(2024, 1, 1)
    for i in range(n):
        cat  = random.choice(CATEGORIES)
        prod = random.choice(PRODUCTS[cat])
        lo, hi = PRICE_RANGE[cat]
        price = round(random.uniform(lo, hi), 2)
        qty   = random.randint(1, 10)
        date  = start + timedelta(days=random.randint(0, 364))
        transactions.append({
            "id":       i + 1,
            "date":     date.strftime("%Y-%m-%d"),
            "month":    date.strftime("%B"),
            "month_num": date.month,
            "category": cat,
            "product":  prod,
            "region":   random.choice(REGIONS),
            "price":    price,
            "quantity": qty,
            "revenue":  round(price * qty, 2),
            "cost":     round(price * qty * random.uniform(0.45, 0.70), 2),
        })
    return transactions

# ── Analysis Functions ─────────────────────────────────────────────────────────
def kpi_summary(txns):
    total_rev  = sum(t["revenue"] for t in txns)
    total_cost = sum(t["cost"]    for t in txns)
    profit     = total_rev - total_cost
    margin     = (profit / total_rev * 100) if total_rev else 0
    return {
        "total_revenue":    round(total_rev,  2),
        "total_cost":       round(total_cost, 2),
        "gross_profit":     round(profit,     2),
        "profit_margin":    round(margin,     1),
        "total_orders":     len(txns),
        "avg_order_value":  round(total_rev / len(txns), 2),
        "total_units_sold": sum(t["quantity"] for t in txns),
    }

def revenue_by_month(txns):
    months_order = ["January","February","March","April","May","June",
                    "July","August","September","October","November","December"]
    agg = defaultdict(lambda: {"revenue": 0, "orders": 0})
    for t in txns:
        agg[t["month"]]["revenue"] += t["revenue"]
        agg[t["month"]]["orders"]  += 1
    return [
        {"month": m, "revenue": round(agg[m]["revenue"], 2), "orders": agg[m]["orders"]}
        for m in months_order if m in agg
    ]

def revenue_by_category(txns):
    agg = defaultdict(lambda: {"revenue": 0, "profit": 0, "units": 0, "orders": 0})
    for t in txns:
        c = t["category"]
        agg[c]["revenue"] += t["revenue"]
        agg[c]["profit"]  += t["revenue"] - t["cost"]
        agg[c]["units"]   += t["quantity"]
        agg[c]["orders"]  += 1
    return sorted(
        [{"category": k, "revenue": round(v["revenue"],2),
          "profit": round(v["profit"],2), "units": v["units"], "orders": v["orders"]}
         for k, v in agg.items()],
        key=lambda x: x["revenue"], reverse=True
    )

def revenue_by_region(txns):
    agg = defaultdict(lambda: {"revenue": 0, "orders": 0})
    for t in txns:
        agg[t["region"]]["revenue"] += t["revenue"]
        agg[t["region"]]["orders"]  += 1
    return sorted(
        [{"region": k, "revenue": round(v["revenue"],2), "orders": v["orders"]}
         for k, v in agg.items()],
        key=lambda x: x["revenue"], reverse=True
    )

def top_products(txns, n=10):
    agg = defaultdict(lambda: {"revenue": 0, "units": 0, "category": ""})
    for t in txns:
        key = t["product"]
        agg[key]["revenue"]  += t["revenue"]
        agg[key]["units"]    += t["quantity"]
        agg[key]["category"]  = t["category"]
    return sorted(
        [{"product": k, "revenue": round(v["revenue"],2),
          "units": v["units"], "category": v["category"]}
         for k, v in agg.items()],
        key=lambda x: x["revenue"], reverse=True
    )[:n]

def weekly_trend(txns):
    agg = defaultdict(float)
    for t in txns:
        d = datetime.strptime(t["date"], "%Y-%m-%d")
        week = f"W{d.isocalendar()[1]:02d}"
        agg[week] += t["revenue"]
    return [{"week": k, "revenue": round(v, 2)} for k, v in sorted(agg.items())]

def category_monthly_heatmap(txns):
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_map = {f"{i+1:02d}": m for i, m in enumerate(months)}
    agg = defaultdict(lambda: defaultdict(float))
    for t in txns:
        mo = t["date"][5:7]
        agg[t["category"]][month_map[mo]] += t["revenue"]
    return {cat: {m: round(agg[cat].get(m, 0), 2) for m in months} for cat in CATEGORIES}

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("🛒  Retail Data Analysis — generating data...")
    txns = generate_transactions(1200)

    payload = {
        "generated_at":     datetime.now().isoformat(),
        "record_count":     len(txns),
        "kpis":             kpi_summary(txns),
        "monthly_revenue":  revenue_by_month(txns),
        "category_revenue": revenue_by_category(txns),
        "region_revenue":   revenue_by_region(txns),
        "top_products":     top_products(txns, 10),
        "weekly_trend":     weekly_trend(txns),
        "heatmap":          category_monthly_heatmap(txns),
        "transactions":     txns[:50],   # sample for table display
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(payload, f, indent=2)

    k = payload["kpis"]
    print(f"✅  Analysis complete — {len(txns)} transactions processed")
    print(f"   Total Revenue  : ₹{k['total_revenue']:,.2f}")
    print(f"   Gross Profit   : ₹{k['gross_profit']:,.2f}")
    print(f"   Profit Margin  : {k['profit_margin']}%")
    print(f"   Avg Order Value: ₹{k['avg_order_value']:,.2f}")
    print(f"   Output JSON    : {OUTPUT_JSON}")
    return payload

if __name__ == "__main__":
    main()
