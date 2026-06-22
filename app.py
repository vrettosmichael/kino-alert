import requests

API_URL = "https://api.opap.gr/draws/v3.0/1100/last/1"

try:
    res = requests.get(API_URL, timeout=20)
    data = res.json()

    print("TYPE:")
    print(type(data))

    print("DATA:")
    print(data)

except Exception as e:
    print("Error:", e)
