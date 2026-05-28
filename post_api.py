import requests
import json

# create a new post
url = "https://jsonplaceholder.typicode.com/posts"

payload = {
    "title": "My First Post",
    "body": "This is the body of my post",
    "userId": 1
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Status: {response.status_code}")
print(f"Created post ID: {data['id']}")
print(f"Title: {data['title']}")

# update a post
url2 = "https://jsonplaceholder.typicode.com/posts/1"
update_payload = {
    "title": "Updated Title",
    "body": "Updated body",
    "userId": 1
}

response2 = requests.put(url2, json=update_payload)
print(f"\nUpdate status: {response2.status_code}")
print(f"Updated title: {response2.json()['title']}")

# delete a post
response3 = requests.delete(url2)
print(f"\nDelete status: {response3.status_code}")
