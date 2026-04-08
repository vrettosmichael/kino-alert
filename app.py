import os
import requests
from datetime import datetime

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
    res = requests.get("https://api.opap.gr/draws/v3.0/1100/last-result-and-active")
    data = res.json()

    draw_id = data["drawId"]
    draw_time_raw = data["drawTime"]

    draw_time = datetime.fromtimestamp(draw_time_raw / 1000).strftime("%H:%M")
    last_digit = draw_id % 10

    if last_digit == 3 or last_digit == 4:
        send_message(f"🚨 ΚΙΝΟ ALERT\nΣειρά: {last_digit}\nΏρα: {draw_time}")

except Exception as e:
    print("Error:", e)
