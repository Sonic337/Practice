import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    result = requests.post(url, json={"chat_id": chat_id, "text": text})
    print(result.status_code, result.json())

def check_token(symbol):
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "allMids"}
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get(symbol)

symbol = "QNT"

print(f"Monitoring {symbol} on Hyperliquid...")
send_telegram(f"👀 Monitoring {symbol} on Hyperliquid... not live yet.")

while True:
    price = check_token(symbol)
    if price:
        while True:
            send_telegram(f"🚨🚨🚨 {symbol} IS LIVE! Price: ${price} — GO GO GO!")
            time.sleep(1)
    else:
        send_telegram(f"👀 {symbol} not live yet, checking again in 2 mins...")
        print("Not live yet...")
        time.sleep(120)
