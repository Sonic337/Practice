import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

CONTRACT = "0x4a220e6096b25eadb88358cb44068a3248254675"
RPC_URL = "https://rpc.hyperliquid.xyz/evm"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def get_token_balance():
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": CONTRACT,
            "data": "0x18160ddd"
        }, "latest"],
        "id": 1
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json().get("result", "0x0")
    return int(result, 16)

print("Monitoring QNT on HyperEVM...")
send_telegram("👀 Monitoring QNT on HyperEVM... checking total supply activity.")

last_supply = None

while True:
    try:
        supply = get_token_balance()
        print(f"Total supply: {supply}")
        if last_supply is not None and supply != last_supply:
            send_telegram(f"🚨 QNT supply changed! Was: {last_supply} Now: {supply}")
        last_supply = supply
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(30)

