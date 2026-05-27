from datetime import datetime, timedelta

now = datetime.now()
print("Now:", now)
print("Formatted:", now.strftime("%Y-%m-%d %H:%M:%S"))
print("Day:", now.strftime("%A"))
print("Date only:", now.strftime("%d %B %Y"))

# add and subtract time
tomorrow = now + timedelta(days=1)
yesterday = now - timedelta(days=1)
one_hour_ago = now - timedelta(hours=1)

print("Tomorrow:", tomorrow.strftime("%Y-%m-%d"))
print("Yesterday:", yesterday.strftime("%Y-%m-%d"))
print("One hour ago:", one_hour_ago.strftime("%H:%M:%S"))

# days until harish's birthday
birthday = datetime(2026, 6, 5)
days_left = (birthday - now).days
print(f"Days until Harish's birthday: {days_left}")
