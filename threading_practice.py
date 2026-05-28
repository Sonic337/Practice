import threading
import time
import requests

def fetch_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()
    temp = data["current_condition"][0]["temp_C"]
    print(f"{city}: {temp}°C")

cities = ["Pune", "Mumbai", "Delhi", "Dubai", "London"]

print("Fetching sequentially...")
start = time.time()
for city in cities:
    fetch_weather(city)
print(f"Sequential time: {time.time() - start:.2f}s")

print("\nFetching with threads...")
start = time.time()
threads = []
for city in cities:
    t = threading.Thread(target=fetch_weather, args=(city,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
print(f"Threaded time: {time.time() - start:.2f}s")
