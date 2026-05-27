import requests
import os
from dotenv import load_dotenv

load_dotenv()

city = os.environ.get("CITY")

if not city:
    raise ValueError("CITY not set in .env file")

try:
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    temp = data["current_condition"][0]["temp_C"]
    print(f"Temperature in {city}: {temp}°C")

except requests.exceptions.Timeout:
    print("Request timed out")

except requests.exceptions.HTTPError as e:
    print("HTTP error: " + str(e))

except Exception as e:
    print("Something went wrong: " + str(e))

