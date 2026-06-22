import os
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

API_URL = "https://api.opap.gr/draws/v3.0/1100/last-result-and-active"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, data=data)
    print(response.status_code)
    print(response.text)


def group_number(n):
    if 1 <= n <= 5:
        return "LOW"
    return "HIGH"


try:
    res = requests.get(API_URL, timeout=20)
    data = res.json()

    last_draw = data["last"]
    draw_id = last_draw["drawId"]
    draw_time_raw = last_draw["drawTime"]
    draw_time = datetime.fromtimestamp(draw_time_raw / 1000).strftime("%H:%M")

    numbers = last_draw["winningNumbers"]["list"]

    small_numbers = [n for n in numbers if 1 <= n <= 10]

    print("Draw:", draw_id)
    print("Time:", draw_time)
    print("Numbers 1-10:", small_numbers)

    if len(small_numbers) >= 6:
        last_5 = small_numbers[-6:-1]
        sixth = small_numbers[-1]

        groups = [group_number(n) for n in last_5]

        if all(g == "LOW" for g in groups) or all(g == "HIGH" for g in groups):
            pattern_group = groups[0]
            sixth_group = group_number(sixth)

            message = (
                "🚨 KINO ALERT\n\n"
                f"Κλήρωση: {draw_id}\n"
                f"Ώρα: {draw_time}\n\n"
                f"5 συνεχόμενα {pattern_group}\n"
                f"Νούμερα: {', '.join(map(str, last_5))}\n\n"
                f"6ο νούμερο: {sixth} ({sixth_group})"
            )

            send_message(message)
        else:
            print("No 5 LOW/HIGH pattern found.")
    else:
        print("Not enough numbers between 1 and 10.")

except Exception as e:
    print("Error:", e)
