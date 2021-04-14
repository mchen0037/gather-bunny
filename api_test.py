import requests
import os

data = requests.get("https://gather.town/api/getMap",
    params={
        "apiKey": os.environ["GATHER_API_KEY"],
        "spaceId": "Uu7dRIJ7BdzD44NS\\party",
        "mapId": "homeroom"
    }
)

# print(data.json())
new_map = data.json()
x_val = new_map["objects"][-1]["x"]
for i in range(0, 5):
    new_map["objects"][-1]["x"] = x_val - 1
    x_val = x_val - 1
    req = requests.post("https://gather.town/api/setMap",
        json={
            "apiKey": os.environ["GATHER_API_KEY"],
            "spaceId": "Uu7dRIJ7BdzD44NS\\party",
            "mapId": "homeroom",
            "mapContent": new_map
        }
)

print(req.text)
