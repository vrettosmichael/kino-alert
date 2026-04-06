import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, data=data)
print(response.status_code)
print(response.text)

try:
    res = requests.get("https://api.opap.gr/draws/v3.0/1100/last-result")
    data = res.json()

    draw_id = data["drawId"]
    draw_time = data["drawTime"]

    last_digit = draw_id % 10

    send_message(f"✅ TEST ΚΙΝΟ\nΣειρά: {last_digit}\nΏρα: {draw_time}")

except Exception as e:
    print("Error:", e)
