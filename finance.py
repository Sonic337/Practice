import json
import os
import sys
import csv
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "finance.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_entry(etype, amount, category, note=""):
    db = load_db()
    entry = {
        "type": etype,
        "amount": float(amount),
        "category": category,
        "note": note,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.append(entry)
    save_db(db)
    print(f"Added: {etype} Rs{amount} | {category} | {note}")

def balance():
    db = load_db()
    income = sum(e["amount"] for e in db if e["type"] == "income")
    expense = sum(e["amount"] for e in db if e["type"] == "expense")
    print(f"Total Income:  Rs{income:,.2f}")
    print(f"Total Expense: Rs{expense:,.2f}")
    print(f"Balance:       Rs{income - expense:,.2f}")

def summary():
    db = load_db()
    categories = {}
    for e in db:
        if e["type"] == "expense":
            cat = e["category"]
            categories[cat] = categories.get(cat, 0) + e["amount"]
    print("Expense breakdown:")
    for cat, total in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: Rs{total:,.2f}")

def list_all():
    db = load_db()
    for e in db:
        print(f"{e['date']} | {e['type'].upper()} | Rs{e['amount']} | {e['category']} | {e['note']}")

def export_csv():
    db = load_db()
    with open("finance_export.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "type", "amount", "category", "note"])
        writer.writeheader()
        writer.writerows(db)
    print("Exported to finance_export.csv")

args = sys.argv
if len(args) < 2:
    print("Usage:")
    print("  finance income <amount> <category> <note>")
    print("  finance expense <amount> <category> <note>")
    print("  finance balance")
    print("  finance summary")
    print("  finance list")
    print("  finance export")
elif args[1] == "income":
    add_entry("income", args[2], args[3], " ".join(args[4:]))
elif args[1] == "expense":
    add_entry("expense", args[2], args[3], " ".join(args[4:]))
elif args[1] == "balance":
    balance()
elif args[1] == "summary":
    summary()
elif args[1] == "list":
    list_all()
elif args[1] == "export":
    export_csv()

