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

def monthly():
    db = load_db()
    months = {}
    for e in db:
        month = e["date"][:7]
        if month not in months:
            months[month] = {"income": 0, "expense": 0}
        months[month][e["type"]] += e["amount"]
    print("Monthly breakdown:")
    for month in sorted(months.keys()):
        m = months[month]
        print(f"  {month} | Income: Rs{m['income']:,.2f} | Expense: Rs{m['expense']:,.2f} | Balance: Rs{m['income']-m['expense']:,.2f}")
def set_budget(category, amount):
    budgets = {}
    if os.path.exists("budgets.json"):
        with open("budgets.json", "r") as f:
            budgets = json.load(f)
    budgets[category] = float(amount)
    with open("budgets.json", "w") as f:
        json.dump(budgets, f, indent=4)
    print(f"Budget set: {category} = Rs{float(amount):,.2f}")

def check_budgets():
    if not os.path.exists("budgets.json"):
        print("No budgets set.")
        return
    with open("budgets.json", "r") as f:
        budgets = json.load(f)
    db = load_db()
    current_month = datetime.now().strftime("%Y-%m")
    categories = {}
    for e in db:
        if e["type"] == "expense" and e["date"][:7] == current_month:
            cat = e["category"]
            categories[cat] = categories.get(cat, 0) + e["amount"]
    print("Budget status this month:")
    for cat, limit in budgets.items():
        spent = categories.get(cat, 0)
        status = "OVER BUDGET" if spent > limit else "ok"
        print(f"  {cat}: Rs{spent:,.2f} / Rs{limit:,.2f} [{status}]")

def search(keyword):
    db = load_db()
    results = [e for e in db if keyword.lower() in e["note"].lower() or keyword.lower() in e["category"].lower()]
    if results:
        for e in results:
            print(f"{e['date']} | {e['type'].upper()} | Rs{e['amount']} | {e['category']} | {e['note']}")
    else:
        print(f"No results for: {keyword}")

def chart():
    db = load_db()
    categories = {}
    for e in db:
        if e["type"] == "expense":
            cat = e["category"]
            categories[cat] = categories.get(cat, 0) + e["amount"]
    if not categories:
        print("No expenses yet.")
        return
    max_amount = max(categories.values())
    print("\nExpense Chart:")
    for cat, total in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((total / max_amount) * 40)
        bar = "█" * bar_length
        print(f"  {cat:<15} {bar} Rs{total:,.2f}")

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
def add_recurring(etype, amount, category, note=""):
    recurring = []
    if os.path.exists("recurring.json"):
        with open("recurring.json", "r") as f:
            recurring = json.load(f)
    recurring.append({
        "type": etype,
        "amount": float(amount),
        "category": category,
        "note": note
    })
    with open("recurring.json", "w") as f:
        json.dump(recurring, f, indent=4)
    print(f"Recurring added: {etype} Rs{amount} | {category}")

def apply_recurring():
    if not os.path.exists("recurring.json"):
        print("No recurring transactions set.")
        return
    with open("recurring.json", "r") as f:
        recurring = json.load(f)
    for e in recurring:
        add_entry(e["type"], e["amount"], e["category"], e["note"] + " (recurring)")
    print(f"Applied {len(recurring)} recurring transactions.")

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
elif args[1] == "monthly":
    monthly()
elif args[1] == "budget":
    set_budget(args[2], args[3])
elif args[1] == "checkbudget":
    check_budgets()
elif args[1] == "search":
    search(" ".join(args[2:]))
elif args[1] == "chart":
    chart()
elif args[1] == "recurring":
    add_recurring(args[2], args[3], args[4], " ".join(args[5:]))
elif args[1] == "applyrecurring":
    apply_recurring()
