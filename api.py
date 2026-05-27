import urllib.request
import json

url = "https://jsonplaceholder.typicode.com/todos/1"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    print(data)
    print("Title: " + data["title"])
    print("Completed: " + str(data["completed"]))

