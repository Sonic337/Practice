import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def check_qnt():
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "allMids"}
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get("QNT")

print("Monitoring QNT on Hyperliquid...")
send_telegram("👀 Monitoring QNT on Hyperliquid... not live yet.")

while True:
    price = check_qnt()
    if price:
        for i in range(20):
            send_telegram(f"🚨🚨🚨 QNT IS LIVE! Price: ${price} — GO GO GO!")
            time.sleep(2)
        break
    else:
        print("Not live yet...")
        time.sleep(30)
