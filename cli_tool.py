import sys
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()
    temp = data["current_condition"][0]["temp_C"]
    desc = data["current_condition"][0]["weatherDesc"][0]["value"]
    print(f"{city}: {temp}°C, {desc}")

def help():
    print("Usage:")
    print("  python3 cli_tool.py weather <city>")
    print("  python3 cli_tool.py help")

if len(sys.argv) < 2:
    help()
elif sys.argv[1] == "weather":
    if len(sys.argv) < 3:
        print("Provide a city name")
    else:
        weather(sys.argv[2])
elif sys.argv[1] == "help":
    help()
else:
    print(f"Unknown command: {sys.argv[1]}")
    help()
