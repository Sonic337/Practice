import json
import os
import sys

DB_FILE = os.path.join(os.path.dirname(__file__), "restaurants.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_restaurant(name):
    db = load_db()
    cuisine = input("Cuisine: ")
    area = input("Area: ")
    phone = input("Phone: ")
    owner = input("Owner (optional): ")
    db.append({
        "name": name,
        "cuisine": cuisine,
        "area": area,
        "phone": phone,
        "owner": owner,
        "halal": "yes"
    })
    save_db(db)
    print(f"Added: {name}")

def search_by_cuisine(cuisine):
    db = load_db()
    results = [r for r in db if cuisine.lower() in r["cuisine"].lower()]
    if results:
        for r in results:
            print(f"{r['name']} | {r['area']} | {r['phone']}")
    else:
        print(f"No restaurants found for: {cuisine}")

def search_by_name(name):
    db = load_db()
    results = [r for r in db if name.lower() in r["name"].lower()]
    if results:
        for r in results:
            print(f"{r['name']} | Cuisine: {r['cuisine']} | {r['area']}")
    else:
        print(f"Not found: {name}")

def list_all():
    db = load_db()
    for r in db:
        print(f"{r['name']} | {r['cuisine']} | {r['area']}")

if len(sys.argv) < 2:
    print("Usage:")
    print("  restaurants add <name>")
    print("  restaurants cuisine <cuisine>")
    print("  restaurants search <name>")
    print("  restaurants list")
elif sys.argv[1] == "add":
    add_restaurant(" ".join(sys.argv[2:]))
elif sys.argv[1] == "cuisine":
    search_by_cuisine(" ".join(sys.argv[2:]))
elif sys.argv[1] == "search":
    search_by_name(" ".join(sys.argv[2:]))
elif sys.argv[1] == "list":
    list_all()
