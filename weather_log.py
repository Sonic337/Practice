import requests
from datetime import datetime

city = "Pune"
url = f"https://wttr.in/{city}?format=j1"

response = requests.get(url)
data = response.json()

temp = data["current_condition"][0]["temp_C"]
description = data["current_condition"][0]["weatherDesc"][0]["value"]
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

log_entry = f"{now} | {city} | {temp}°C | {description}\n"

with open("weather_log.txt", "a") as f:
    f.write(log_entry)

print("Logged: " + log_entry)

