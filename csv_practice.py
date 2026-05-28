import csv
from datetime import datetime

# write a csv
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "city", "temp", "condition"])
    writer.writerow(["2026-05-28", "Pune", "36", "Sunny"])
    writer.writerow(["2026-05-28", "Mumbai", "34", "Cloudy"])
    writer.writerow(["2026-05-28", "Delhi", "40", "Hazy"])

# read a csv
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['city']}: {row['temp']}°C, {row['condition']}")

