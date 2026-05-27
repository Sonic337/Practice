import os

api_key = os.environ.get("MY_API_KEY")

if api_key:
    print("Key found: " + api_key[:5] + "...")
else:
    print("No API key found")

