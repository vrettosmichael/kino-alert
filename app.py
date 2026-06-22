import os
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

GAME_ID = 1100
API_URL = f"https://api.opap.gr/draws/v3.0/{GAME_ID}/last/20"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=data)
    print(response.status_code)
    print(response.text)


def calculate_s_value(numbers):
    decades = set()
    for num in numbers:
        decade = (num - 1) // 10 + 1
        decades.add(decade)
    return len(decades)


def group_s(s_value):
    return "LOW" if 1 <= s_value <= 5 else "HIGH"


try:
    res = requests.get(API_URL, timeout=20)
    data = res.json()

    # Το API συνήθως επιστρέφει λίστα απευθείας, όχι {"content": ...}
    if isinstance(data, list):
        draws = data
    elif isinstance(data, dict) and "content" in data:
        draws = data["content"]
    else:
        print("Unexpected API format:")
        print(data)
        raise Exception("Unknown API response format")

    results = []

    for draw in draws:
        draw_id = draw["drawId"]
        draw_time_raw = draw["drawTime"]
        draw_time = datetime.fromtimestamp(draw_time_raw / 1000).strftime("%H:%M")
        numbers = draw["winningNumbers"]["list"]

        s_value = calculate_s_value(numbers)

        results.append({
            "draw_id": draw_id,
            "time": draw_time,
            "s": s_value,
            "group": group_s(s_value)
        })

    results = sorted(results, key=lambda x: x["draw_id"])

    print("Last S values:")
    for r in results[-6:]:
        print(r)

    if len(results) >= 6:
        last_5 = results[-6:-1]
        current_6th = results[-1]

        groups = [r["group"] for r in last_5]

        if all(g == "LOW" for g in groups) or all(g == "HIGH" for g in groups):
            pattern_group = groups[0]

            message = (
                "🚨 KINO ALERT\n\n"
                f"5 συνεχόμενα {pattern_group}\n\n"
                f"1) {last_5[0]['time']} → Σ {last_5[0]['s']}\n"
                f"2) {last_5[1]['time']} → Σ {last_5[1]['s']}\n"
                f"3) {last_5[2]['time']} → Σ {last_5[2]['s']}\n"
                f"4) {last_5[3]['time']} → Σ {last_5[3]['s']}\n"
                f"5) {last_5[4]['time']} → Σ {last_5[4]['s']}\n\n"
                f"6ο τώρα:\n"
                f"{current_6th['time']} → Σ {current_6th['s']} ({current_6th['group']})"
            )

            send_message(message)
        else:
            print("No 5 LOW/HIGH pattern found.")
    else:
        print("Not enough draws.")

except Exception as e:
    print("Error:", e)
