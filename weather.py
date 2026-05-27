import requests

city = "Pune"
url = f"https://wttr.in/{city}?format=j1"

response = requests.get(url)
data = response.json()

temp = data["current_condition"][0]["temp_C"]
feels_like = data["current_condition"][0]["FeelsLikeC"]
description = data["current_condition"][0]["weatherDesc"][0]["value"]

print(f"City: {city}")
print(f"Temperature: {temp}°C")
print(f"Feels like: {feels_like}°C")
print(f"Condition: {description}")
