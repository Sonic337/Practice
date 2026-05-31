import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://mainnet.zklighter.elliot.ai"
ACCOUNT_URL = f"{BASE_URL}/api/v1/account"

WALLET = os.environ.get("LIGHTER_WALLET")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def fetch_account(wallet):
    response = requests.get(
        ACCOUNT_URL,
        params={"by": "l1_address", "value": wallet, "active_only": "true"},
        timeout=15,
    )
    if response.status_code != 200:
        print(f"Lighter API error: {response.status_code}")
        sys.exit(1)

    data = response.json()
    if data.get("code") != 200:
        print(f"Lighter API error: {data.get('message', data)}")
        sys.exit(1)

    accounts = data.get("accounts") or []
    if not accounts:
        print(f"No Lighter account found for {wallet}")
        sys.exit(1)
    return accounts[0]


def parse_positions(account):
    positions = []
    for pos in account.get("positions") or []:
        size_abs = float(pos.get("position", 0))
        if size_abs == 0:
            continue

        sign = int(pos.get("sign", 1))
        size = sign * size_abs
        entry_px = float(pos["avg_entry_price"]) if pos.get("avg_entry_price") else None
        position_value = float(pos.get("position_value", 0))
        unrealized_pnl = float(pos.get("unrealized_pnl", 0))
        mark_px = abs(position_value / size_abs) if size_abs else None

        positions.append(
            {
                "market": pos.get("symbol", "?"),
                "size": size,
                "entry_px": entry_px,
                "mark_px": mark_px,
                "unrealized_pnl": unrealized_pnl,
            }
        )
    return positions


def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        timeout=15,
    )
    if response.status_code != 200:
        print(f"Telegram error: {response.status_code} {response.text}")
        return False
    return True


def format_pnl_message(positions, total_pnl, title, starting_pnl=None, loss_floor=None):
    lines = [f"{title}\n", f"Total unrealized PNL: ${total_pnl:+,.2f}"]
    if starting_pnl is not None:
        lines.append(f"Started at: ${starting_pnl:+,.2f}")
    if loss_floor is not None:
        lines.append(f"Alert floor: ${loss_floor:+,.2f}")
    lines.append("")
    for p in positions:
        entry = f"${p['entry_px']:,.4f}" if p["entry_px"] is not None else "N/A"
        lines.append(
            f"• {p['market']}: ${p['unrealized_pnl']:+,.2f} "
            f"(size {p['size']:g}, entry {entry})"
        )
    return "\n".join(lines)


def get_snapshot(wallet):
    account = fetch_account(wallet)
    account_value = account.get("total_asset_value") or account.get("collateral")
    positions = parse_positions(account)
    total_pnl = sum(p["unrealized_pnl"] for p in positions)
    return positions, account_value, total_pnl


def print_positions(positions, account_value=None):
    if not positions:
        print("No open positions on Lighter.")
        return 0.0

    print(
        f"\n{'Market':<14} {'Size':>12} {'Entry':>14} {'Mark':>14} {'Unrealized PNL':>16}"
    )
    print("-" * 74)

    total_pnl = 0.0
    for p in positions:
        total_pnl += p["unrealized_pnl"]
        entry = f"${p['entry_px']:,.4f}" if p["entry_px"] is not None else "N/A"
        mark = f"${p['mark_px']:,.4f}" if p["mark_px"] is not None else "N/A"
        print(
            f"{p['market']:<14} {p['size']:>12g} {entry:>14} {mark:>14} "
            f"${p['unrealized_pnl']:>+14,.2f}"
        )

    print("-" * 74)
    print(f"{'TOTAL':<14} {'':>12} {'':>14} {'':>14} ${total_pnl:>+14,.2f}")
    if account_value is not None:
        print(f"Account value: ${float(account_value):,.2f}")
    return total_pnl


def show_once(wallet):
    positions, account_value, _ = get_snapshot(wallet)
    print(f"Lighter — {wallet}")
    return print_positions(positions, account_value)


def watch(wallet, drop_threshold):
    refresh_secs = 30
    pnl_update_interval = 30 * 60
    starting_pnl = None
    loss_floor = None
    alert_active = False
    last_pnl_update = None

    print(
        f"Watching Lighter positions (refresh {refresh_secs}s, "
        f"PNL update every 30m, alert on ${drop_threshold:,.2f} drop from start)"
    )

    while True:
        positions, account_value, total_pnl = get_snapshot(wallet)

        if starting_pnl is None:
            starting_pnl = total_pnl
            loss_floor = starting_pnl - drop_threshold
            print(f"Starting PNL: ${starting_pnl:+,.2f}")
            print(f"Loss alert if PNL drops to ${loss_floor:+,.2f} or below")

            msg = format_pnl_message(
                positions,
                total_pnl,
                "👀 Lighter watch started",
                starting_pnl=starting_pnl,
                loss_floor=loss_floor,
            )
            if send_telegram(msg):
                print("Telegram watch-start message sent.")
            last_pnl_update = time.monotonic()

        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Lighter — {wallet}")
        print_positions(positions, account_value)

        now = time.monotonic()
        if now - last_pnl_update >= pnl_update_interval:
            msg = format_pnl_message(
                positions,
                total_pnl,
                "📊 Lighter PNL update",
                starting_pnl=starting_pnl,
                loss_floor=loss_floor,
            )
            if send_telegram(msg):
                print("\n📊 Telegram PNL update sent.")
            last_pnl_update = now

        if total_pnl <= loss_floor and not alert_active:
            drop = starting_pnl - total_pnl
            msg = format_pnl_message(
                positions,
                total_pnl,
                f"🚨 Lighter PNL alert (down ${drop:,.2f} from start)",
                starting_pnl=starting_pnl,
                loss_floor=loss_floor,
            )
            if send_telegram(msg):
                print("\n⚠️  Telegram loss alert sent.")
            alert_active = True
        elif total_pnl > loss_floor:
            alert_active = False

        time.sleep(refresh_secs)


def print_usage():
    print("Usage:")
    print("  lighter_pnl.py")
    print("  lighter_pnl.py watch <drop_amount>")
    print("\nExamples:")
    print("  lighter_pnl.py")
    print("  lighter_pnl.py watch 10    # alert if PNL drops $10 from value at watch start")


def main():
    if not WALLET:
        print("Missing LIGHTER_WALLET in .env")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        show_once(WALLET)
    elif args[0] == "watch":
        if len(args) < 2:
            print("Usage: lighter_pnl.py watch <drop_amount>")
            sys.exit(1)
        watch(WALLET, float(args[1]))
    else:
        print(f"Unknown command: {args[0]}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
