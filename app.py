import requests

url = "https://api.opap.gr/draws/v3.0/1100/last-result-and-active"

r = requests.get(url)
data = r.json()

print(data)
