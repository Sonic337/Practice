import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OMDB_API_KEY")

def search_movie(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "False":
        print(f"Movie not found: {title}")
        return

    print(f"\n{data['Title']} ({data['Year']})")
    print(f"Genre: {data['Genre']}")
    print(f"Director: {data['Director']}")
    print(f"Cast: {data['Actors']}")
    print(f"Rating: {data['imdbRating']}/10")
    print(f"Plot: {data['Plot']}")

if len(sys.argv) > 1:
    search_movie(" ".join(sys.argv[1:]))
else:
    print("Usage: movies <movie title>")
