import requests
import sys

def get_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)
    
    if response.status_code == 404:
        print(f"Pokemon '{name}' not found")
        return
    
    data = response.json()
    
    name = data["name"].capitalize()
    height = data["height"]
    weight = data["weight"]
    types = [t["type"]["name"] for t in data["types"]]
    abilities = [a["ability"]["name"] for a in data["abilities"]]
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    
    print(f"\n{name}")
    print(f"Type: {', '.join(types)}")
    print(f"Height: {height/10}m | Weight: {weight/10}kg")
    print(f"Abilities: {', '.join(abilities)}")
    print(f"Stats: HP={stats['hp']} ATK={stats['attack']} DEF={stats['defense']} SPD={stats['speed']}")

if len(sys.argv) > 1:
    get_pokemon(sys.argv[1])
else:
    print("Usage: python3 pokemon.py <pokemon name>")
