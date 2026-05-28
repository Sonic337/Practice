import requests
import sys

def get_coin(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    
    if response.status_code == 404:
        print(f"Coin '{coin_id}' not found")
        return
    
    data = response.json()
    
    name = data["name"]
    symbol = data["symbol"].upper()
    price = data["market_data"]["current_price"]["usd"]
    change_24h = data["market_data"]["price_change_percentage_24h"]
    market_cap = data["market_data"]["market_cap"]["usd"]
    rank = data["market_cap_rank"]
    
    print(f"\n{name} ({symbol})")
    print(f"Rank: #{rank}")
    print(f"Price: ${price:,.2f}")
    print(f"24h Change: {change_24h:.2f}%")
    print(f"Market Cap: ${market_cap:,.0f}")

if len(sys.argv) > 1:
    get_coin(sys.argv[1])
else:
    print("Usage: python3 crypto.py <coin-id>")
    print("Examples: bitcoin, ethereum, solana, hyperliquid")
