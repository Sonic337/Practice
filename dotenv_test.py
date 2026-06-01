from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("MY_API_KEY")
city = os.environ.get("CITY")

if api_key:
    print("Key: " + api_key[:5] + "...")
else:
    print("Key: not set")
print("City: " + (city or "(not set)"))

