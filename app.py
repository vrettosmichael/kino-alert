import time
import requests

TOKEN = "8669405381:AAEsB6LU119YnVq1Cc9_VwL2QcYjSQfUNXQ"
CHAT_ID = "8602975728""

last_draw_id = None

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

while True:
    try:
        res = requests.get("https://api.opap.gr/draws/v3.0/1100/last-result")
        data = res.json()

        draw_id = data["drawId"]
        draw_time = data["drawTime"]

        if draw_id != last_draw_id:
            last_digit = draw_id % 10

            if last_digit == 3 or last_digit == 4:
                send_message(f"🚨 ΚΙΝΟ ALERT\nΣειρά: {last_digit}\nΏρα: {draw_time}")

        last_draw_id = draw_id

    except Exception as e:
        print("Error:", e)

    time.sleep(300)
