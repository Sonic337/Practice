from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("MY_API_KEY")
city = os.environ.get("CITY")

print("Key: " + api_key[:5] + "...")
print("City: " + city)

