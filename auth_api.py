import requests
import os
from dotenv import load_dotenv

load_dotenv()

# simulate an authenticated API call using headers
api_token = os.environ.get("MY_API_KEY") or "demo-token"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json",
}

# using a free public API that accepts headers
url = "https://jsonplaceholder.typicode.com/posts"
response = requests.get(url, headers=headers)
data = response.json()

# print first 3 posts
for post in data[:3]:
    print(f"ID: {post['id']}")
    print(f"Title: {post['title']}")
    print(f"Body: {post['body'][:50]}...")
    print("---")
