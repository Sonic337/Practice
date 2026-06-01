import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

INFO_URL = "https://api.hyperliquid.xyz/info"
DEX = "xyz"

WALLET = os.environ.get("HYPERLIQUID_WALLET")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def mask_wallet(wallet):
    if not wallet or len(wallet) < 10:
        return "(wallet)"
    return f"{wallet[:6]}...{wallet[-4:]}"


def fetch_clearinghouse_state(wallet):
    response = requests.post(
        INFO_URL,
        json={"type": "clearinghouseState", "user": wallet, "dex": DEX},
        timeout=15,
    )
    if response.status_code != 200:
        print(f"Hyperliquid API error: {response.status_code}")
        sys.exit(1)
    return response.json()


def parse_positions(state):
    positions = []
    for item in state.get("assetPositions", []):
        pos = item.get("position", {})
        szi = float(pos.get("szi", 0))
        if szi == 0:
            continue

        entry_px = float(pos["entryPx"]) if pos.get("entryPx") else None
        position_value = float(pos.get("positionValue", 0))
        unrealized_pnl = float(pos.get("unrealizedPnl", 0))
        mark_px = abs(position_value / szi) if szi else None

        positions.append(
            {
                "coin": pos.get("coin", "?"),
                "size": szi,
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
        print(f"Telegram error: {response.status_code}")
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
            f"• {p['coin']}: ${p['unrealized_pnl']:+,.2f} "
            f"(size {p['size']:g}, entry {entry})"
        )
    return "\n".join(lines)


def get_snapshot(wallet):
    state = fetch_clearinghouse_state(wallet)
    account_value = state.get("marginSummary", {}).get("accountValue")
    positions = parse_positions(state)
    total_pnl = sum(p["unrealized_pnl"] for p in positions)
    return positions, account_value, total_pnl


def print_positions(positions, account_value=None):
    if not positions:
        print("No open positions on Hyperliquid xyz.")
        return 0.0

    print(
        f"\n{'Coin':<14} {'Size':>12} {'Entry':>14} {'Mark':>14} {'Unrealized PNL':>16}"
    )
    print("-" * 74)

    total_pnl = 0.0
    for p in positions:
        total_pnl += p["unrealized_pnl"]
        entry = f"${p['entry_px']:,.4f}" if p["entry_px"] is not None else "N/A"
        mark = f"${p['mark_px']:,.4f}" if p["mark_px"] is not None else "N/A"
        print(
            f"{p['coin']:<14} {p['size']:>12g} {entry:>14} {mark:>14} "
            f"${p['unrealized_pnl']:>+14,.2f}"
        )

    print("-" * 74)
    print(f"{'TOTAL':<14} {'':>12} {'':>14} {'':>14} ${total_pnl:>+14,.2f}")
    if account_value is not None:
        print(f"Account value: ${float(account_value):,.2f}")
    return total_pnl


def show_once(wallet):
    positions, account_value, _ = get_snapshot(wallet)
    print(f"Hyperliquid xyz — {mask_wallet(wallet)}")
    return print_positions(positions, account_value)


def watch(wallet, drop_threshold):
    refresh_secs = 30
    pnl_update_interval = 90 * 60
    starting_pnl = None
    loss_floor = None
    alert_active = False
    last_pnl_update = None

    print(
        f"Watching xyz positions (refresh {refresh_secs}s, "
        f"PNL update every 90m, alert on ${drop_threshold:,.2f} drop from start)"
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
                "👀 Hyperliquid xyz watch started",
                starting_pnl=starting_pnl,
                loss_floor=loss_floor,
            )
            if send_telegram(msg):
                print("Telegram watch-start message sent.")
            last_pnl_update = time.monotonic()

        print(
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hyperliquid xyz — {mask_wallet(wallet)}"
        )
        print_positions(positions, account_value)

        now = time.monotonic()
        if now - last_pnl_update >= pnl_update_interval:
            msg = format_pnl_message(
                positions,
                total_pnl,
                "📊 Hyperliquid xyz PNL update",
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
                f"🚨 Hyperliquid xyz PNL alert (down ${drop:,.2f} from start)",
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
    print("  hl_pnl.py")
    print("  hl_pnl.py watch <drop_amount>")
    print("\nExamples:")
    print("  hl_pnl.py")
    print("  hl_pnl.py watch 10    # alert if PNL drops $10 from value at watch start")


def main():
    if not WALLET:
        print("Missing HYPERLIQUID_WALLET in .env")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        show_once(WALLET)
    elif args[0] == "watch":
        if len(args) < 2:
            print("Usage: hl_pnl.py watch <drop_amount>")
            sys.exit(1)
        watch(WALLET, float(args[1]))
    else:
        print(f"Unknown command: {args[0]}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
