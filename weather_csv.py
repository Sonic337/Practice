import requests
import csv
from datetime import datetime

cities = ["Pune", "Mumbai", "Delhi", "Dubai"]
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("weather_data.csv", "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow(["timestamp", "city", "temp_c", "feels_like", "condition"])
    
    for city in cities:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        data = response.json()
        temp = data["current_condition"][0]["temp_C"]
        feels = data["current_condition"][0]["FeelsLikeC"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        writer.writerow([now, city, temp, feels, desc])
        print(f"Logged {city}: {temp}°C")

