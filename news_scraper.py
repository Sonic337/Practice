import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

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


if __name__ == "__main__":
    main()
