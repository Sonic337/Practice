import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "standup_log.json"
STATE_FILE = BASE_DIR / "standup_state.json"

DAILY_HOUR = 9
DAILY_MINUTE = 0
PROMPT = "Good morning! What are you working on today?"


def require_config():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise SystemExit("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env")


def load_json(path, default):
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_log():
    return load_json(LOG_FILE, [])


def append_log(text):
    entries = load_log()
    entries.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "text": text.strip(),
        }
    )
    save_json(LOG_FILE, entries)


def load_state():
    return load_json(
        STATE_FILE,
        {"update_offset": 0, "last_daily_prompt": None, "last_weekly_summary": None},
    )


def save_state(state):
    save_json(STATE_FILE, state)


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_updates(offset):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    response = requests.get(url, params=params, timeout=35)
    response.raise_for_status()
    return response.json().get("result", [])


def is_from_user(message):
    chat = message.get("chat", {})
    if str(chat.get("id")) != str(TELEGRAM_CHAT_ID):
        return False
    if not message.get("text"):
        return False
    if message.get("from", {}).get("is_bot"):
        return False
    return True


def process_updates(state):
    offset = state.get("update_offset", 0)
    for update in get_updates(offset):
        state["update_offset"] = update["update_id"] + 1
        message = update.get("message") or update.get("edited_message")
        if message and is_from_user(message):
            append_log(message["text"])
            send_message("Logged your standup. Have a productive day!")
    save_state(state)


def entries_for_week_ending_sunday(now):
    """Standups from Monday 00:00 through end of Saturday (week before Sunday summary)."""
    days_since_monday = now.weekday()
    this_monday = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_start = this_monday - timedelta(days=7)
    week_end = this_monday

    result = []
    for entry in load_log():
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
        except (KeyError, ValueError):
            continue
        if week_start <= ts < week_end:
            result.append(entry)
    return sorted(result, key=lambda e: e["timestamp"])


def format_weekly_summary(entries):
    if not entries:
        return "Weekly standup summary\n\nNo standups logged this week."

    lines = ["Weekly standup summary\n"]
    for entry in entries:
        try:
            day = datetime.fromisoformat(entry["timestamp"]).strftime("%a %b %d")
        except ValueError:
            day = entry.get("timestamp", "?")
        lines.append(f"{day}\n{entry['text']}\n")
    return "\n".join(lines).strip()


def maybe_send_scheduled(state):
    now = datetime.now()
    today = now.date().isoformat()

    if now.hour < DAILY_HOUR or (
        now.hour == DAILY_HOUR and now.minute < DAILY_MINUTE
    ):
        return

    if now.weekday() == 6 and state.get("last_weekly_summary") != today:
        entries = entries_for_week_ending_sunday(now)
        send_message(format_weekly_summary(entries))
        state["last_weekly_summary"] = today

    if state.get("last_daily_prompt") != today:
        send_message(PROMPT)
        state["last_daily_prompt"] = today

    save_state(state)


def main():
    require_config()
    print("Standup bot running. Ctrl+C to stop.")
    state = load_state()

    while True:
        try:
            maybe_send_scheduled(state)
            process_updates(state)
        except requests.RequestException as exc:
            print(f"Telegram error: {exc}")
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopped.")
            break


if __name__ == "__main__":
    main()
