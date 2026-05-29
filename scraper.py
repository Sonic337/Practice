import requests

TRENDING_URL = "https://api.coingecko.com/api/v3/search/trending"
LIMIT = 10


def fetch_trending_coins():
    response = requests.get(TRENDING_URL, timeout=15)
    response.raise_for_status()
    return response.json().get("coins", [])[:LIMIT]


def main():
    coins = fetch_trending_coins()

    if not coins:
        print("No trending coins returned.")
        return

    print(f"Top {len(coins)} trending coins on CoinGecko\n")

    for i, entry in enumerate(coins, start=1):
        coin = entry["item"]
        name = coin["name"]
        symbol = coin["symbol"]
        rank = coin.get("market_cap_rank")
        rank_str = f"#{rank}" if rank is not None else "N/A"

        changes = coin.get("data", {}).get("price_change_percentage_24h", {})
        change_24h = changes.get("usd")
        if change_24h is None:
            change_str = "N/A"
        else:
            sign = "+" if change_24h >= 0 else ""
            change_str = f"{sign}{change_24h:.2f}%"

        print(f"{i}. {name} ({symbol})")
        print(f"   Market cap rank: {rank_str}")
        print(f"   24h change: {change_str}")
        print()


if __name__ == "__main__":
    main()
