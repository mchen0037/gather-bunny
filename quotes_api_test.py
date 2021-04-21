import requests
import os

data = requests.get(
    "https://quotes.rest/qod?language=en"
)

res = data.json()
quote = res['contents']['quotes'][0]['quote']
auth = res['contents']['quotes'][0]['author']

print(quote)
print(auth)
