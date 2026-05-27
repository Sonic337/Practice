import json

# create a python dictionary
person = {
    "name": "Sonic",
    "age": 20,
    "skills": ["git", "python", "terminal"],
    "address": {
        "city": "Pune",
        "country": "India"
    }
}

# convert dictionary to JSON string
json_string = json.dumps(person, indent=4)
print(json_string)

# save JSON to a file
with open("person.json", "w") as f:
    json.dump(person, f, indent=4)

# read JSON from file
with open("person.json", "r") as f:
    loaded = json.load(f)

print(loaded["name"])
print(loaded["skills"][0])
print(loaded["address"]["city"])
