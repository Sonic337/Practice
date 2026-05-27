import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

city = os.environ.get("CITY", "Pune")
token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

url = f"https://wttr.in/{city}?format=j1"
response = requests.get(url)
data = response.json()

temp = data["current_condition"][0]["temp_C"]
description = data["current_condition"][0]["weatherDesc"][0]["value"]
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

message = f"🌤 Weather Update\n{now}\nCity: {city}\nTemp: {temp}°C\nCondition: {description}"

telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
requests.post(telegram_url, json={"chat_id": chat_id, "text": message})
print("Sent to Telegram")

