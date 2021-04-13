import requests
import os

data = requests.get("https://gather.town/api/getMap",
    params={
        'apiKey': os.environ['GATHER_API_KEY'],
        'spaceId': "Uu7dRIJ7BdzD44NS\\party",
        'mapId': "rooftop"
    }
)

print(data.json().keys())
