import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

try:
    # Παίρνει το τελευταίο αποτέλεσμα
    r = requests.get(
        "https://api.opap.gr/draws/v3.0/1100/last-result-and-active",
        timeout=10
    )

    data = r.json()

    print("LATEST DRAW:")
    print(data["last"]["drawId"])

    # ΠΡΟΣΩΡΙΝΟ TEST
    send_message("Teleperformance TEST")

except Exception as e:
    print("ERROR:", e)
