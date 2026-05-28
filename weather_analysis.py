import csv

cities_data = []

with open("weather_data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cities_data.append(row)

# get latest entry per city
latest = {}
for row in cities_data:
    latest[row["city"]] = row

# find hottest city
hottest = max(latest.values(), key=lambda x: int(x["temp_c"]))
coldest = min(latest.values(), key=lambda x: int(x["temp_c"]))

# average temp
avg = sum(int(r["temp_c"]) for r in latest.values()) / len(latest)

print(f"Hottest: {hottest['city']} at {hottest['temp_c']}°C")
print(f"Coldest: {coldest['city']} at {coldest['temp_c']}°C")
print(f"Average: {avg:.1f}°C")
print("\nAll cities:")
for city, data in latest.items():
    print(f"  {city}: {data['temp_c']}°C - {data['condition']}")
