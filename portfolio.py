import json
import os
import sys

import requests
from dotenv import load_dotenv

from crypto import COIN_MAP

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

DB_FILE = os.path.join(os.path.dirname(__file__), "portfolio.json")
PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"


def load_portfolio():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []


def save_portfolio(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def resolve_coin_id(query):
    return COIN_MAP.get(query.lower(), query.lower())


def add_holding(coin, amount, buy_price):
    coin_id = resolve_coin_id(coin)
    amount = float(amount)
    buy_price = float(buy_price)
    portfolio = load_portfolio()

    for entry in portfolio:
        if entry["coin_id"] == coin_id:
            old_amount = entry["amount"]
            old_cost = old_amount * entry["buy_price"]
            new_cost = amount * buy_price
            total_amount = old_amount + amount
            entry["buy_price"] = (old_cost + new_cost) / total_amount
            entry["amount"] = total_amount
            save_portfolio(portfolio)
            print(
                f"Updated {coin_id}: {total_amount:g} @ avg ${entry['buy_price']:,.2f}"
            )
            return

    portfolio.append(
        {
            "coin_id": coin_id,
            "amount": amount,
            "buy_price": buy_price,
        }
    )
    save_portfolio(portfolio)
    print(f"Added {coin_id}: {amount:g} @ ${buy_price:,.2f}")


def remove_holding(coin):
    coin_id = resolve_coin_id(coin)
    portfolio = load_portfolio()
    updated = [e for e in portfolio if e["coin_id"] != coin_id]
    if len(updated) == len(portfolio):
        print(f"No holding for '{coin}'")
        return
    save_portfolio(updated)
    print(f"Removed {coin_id}")


def fetch_prices(coin_ids):
    if not coin_ids:
        return {}
    response = requests.get(
        PRICE_URL,
        params={"ids": ",".join(coin_ids), "vs_currencies": "usd"},
        timeout=15,
    )
    if response.status_code != 200:
        print(f"CoinGecko error: {response.status_code}")
        sys.exit(1)
    return response.json()


def show_portfolio():
    portfolio = load_portfolio()
    if not portfolio:
        print("Portfolio is empty. Add holdings with:")
        print("  portfolio add <coin> <amount> <buy_price>")
        return

    coin_ids = [e["coin_id"] for e in portfolio]
    prices = fetch_prices(coin_ids)

    total_cost = 0.0
    total_value = 0.0

    print(f"\n{'Coin':<18} {'Amount':>12} {'Buy':>12} {'Now':>12} {'Value':>14} {'P/L':>14}")
    print("-" * 86)

    for entry in portfolio:
        coin_id = entry["coin_id"]
        amount = entry["amount"]
        buy_price = entry["buy_price"]
        price_data = prices.get(coin_id, {})
        current_price = price_data.get("usd")

        cost = amount * buy_price
        total_cost += cost

        if current_price is None:
            print(
                f"{coin_id:<18} {amount:>12g} ${buy_price:>10,.2f} "
                f"{'N/A':>12} {'N/A':>14} {'N/A':>14}"
            )
            continue

        value = amount * current_price
        pnl = value - cost
        total_value += value

        print(
            f"{coin_id:<18} {amount:>12g} ${buy_price:>10,.2f} "
            f"${current_price:>10,.2f} ${value:>12,.2f} "
            f"${pnl:>+12,.2f}"
        )

    print("-" * 86)
    total_pnl = total_value - total_cost
    if total_cost > 0:
        pnl_pct = (total_pnl / total_cost) * 100
        print(
            f"{'TOTAL':<18} {'':>12} ${total_cost:>10,.2f} "
            f"{'':>12} ${total_value:>12,.2f} "
            f"${total_pnl:>+12,.2f} ({pnl_pct:+.1f}%)"
        )
    else:
        print(f"{'TOTAL':<42} ${total_value:>12,.2f}")


def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env")
        sys.exit(1)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        timeout=15,
    )
    if response.status_code != 200:
        print(f"Telegram error: {response.status_code} {response.text}")
        sys.exit(1)


def check_alerts(threshold_pct):
    portfolio = load_portfolio()
    if not portfolio:
        print("Portfolio is empty.")
        return

    threshold = float(threshold_pct)
    coin_ids = [e["coin_id"] for e in portfolio]
    prices = fetch_prices(coin_ids)

    alerts = []
    for entry in portfolio:
        coin_id = entry["coin_id"]
        buy_price = entry["buy_price"]
        current_price = prices.get(coin_id, {}).get("usd")
        if current_price is None:
            print(f"Skipping {coin_id}: price unavailable")
            continue

        change_pct = ((current_price - buy_price) / buy_price) * 100
        if abs(change_pct) >= threshold:
            direction = "up" if change_pct > 0 else "down"
            alerts.append(
                (coin_id, change_pct, current_price, buy_price, direction)
            )

    if not alerts:
        print(f"No coins moved ±{threshold:g}% from buy price.")
        return

    lines = [f"🚨 Portfolio alert (±{threshold:g}% threshold)\n"]
    for coin_id, change_pct, current_price, buy_price, direction in alerts:
        lines.append(
            f"• {coin_id}: {change_pct:+.1f}% ({direction})\n"
            f"  Buy ${buy_price:,.2f} → Now ${current_price:,.2f}"
        )
    message = "\n".join(lines)
    send_telegram(message)
    print(f"Sent Telegram alert for {len(alerts)} coin(s):")
    for coin_id, change_pct, _, _, _ in alerts:
        print(f"  {coin_id}: {change_pct:+.1f}%")


def list_holdings():
    portfolio = load_portfolio()
    if not portfolio:
        print("Portfolio is empty.")
        return
    for entry in portfolio:
        cost = entry["amount"] * entry["buy_price"]
        print(
            f"{entry['coin_id']}: {entry['amount']:g} @ "
            f"${entry['buy_price']:,.2f} (cost ${cost:,.2f})"
        )


def print_usage():
    print("Usage:")
    print("  portfolio add <coin> <amount> <buy_price>")
    print("  portfolio remove <coin>")
    print("  portfolio show")
    print("  portfolio list")
    print("  portfolio alert <percent>")
    print("\nExamples:")
    print("  portfolio add btc 0.5 42000")
    print("  portfolio add eth 2 2500")
    print("  portfolio show")
    print("  portfolio alert 10")


args = sys.argv
if len(args) < 2:
    print_usage()
elif args[1] == "add":
    if len(args) < 5:
        print("Usage: portfolio add <coin> <amount> <buy_price>")
    else:
        add_holding(args[2], args[3], args[4])
elif args[1] == "remove":
    if len(args) < 3:
        print("Usage: portfolio remove <coin>")
    else:
        remove_holding(args[2])
elif args[1] in ("show", "balance"):
    show_portfolio()
elif args[1] == "list":
    list_holdings()
elif args[1] == "alert":
    if len(args) < 3:
        print("Usage: portfolio alert <percent>")
    else:
        check_alerts(args[2])
else:
    print(f"Unknown command: {args[1]}")
    print_usage()
