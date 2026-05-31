import os
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests
from dotenv import load_dotenv

load_dotenv()

RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"
LIMIT = 10


def fetch_headlines():
    response = requests.get(RSS_URL, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    channel = root.find("channel")
    if channel is None:
        return []

    headlines = []
    for item in channel.findall("item")[:LIMIT]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()

        try:
            pub_date = parsedate_to_datetime(pub_date_raw).strftime("%Y-%m-%d %H:%M %Z")
        except (TypeError, ValueError):
            pub_date = pub_date_raw or "Unknown"

        headlines.append({"title": title, "link": link, "pub_date": pub_date})

    return headlines


def send_to_telegram(headlines):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise ValueError("TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    top3 = headlines[:3]
    lines = ["*Top 3 Crypto Headlines*\n"]
    for i, h in enumerate(top3, start=1):
        lines.append(f"{i}. [{h['title']}]({h['link']})\n   _{h['pub_date']}_")
    message = "\n".join(lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=15)
    response.raise_for_status()
    return response.json()


def main():
    headlines = fetch_headlines()

    if not headlines:
        print("No headlines returned.")
        return

    print(f"Top {len(headlines)} crypto news headlines from CoinDesk\n")

    for i, headline in enumerate(headlines, start=1):
        print(f"{i}. {headline['title']}")
        print(f"   Published: {headline['pub_date']}")
        print(f"   Link: {headline['link']}")
        print()

    send_to_telegram(headlines)
    print("Top 3 headlines sent to Telegram.")


if __name__ == "__main__":
    main()
