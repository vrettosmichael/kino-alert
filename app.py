import os
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

API_URL = "https://api.opap.gr/draws/v3.0/1100/last/30"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=data)
    print(response.status_code)
    print(response.text)


def calculate_s_value(numbers):
    counts = {}
    first_seen = {}

    for index, num in enumerate(numbers):
        decade = (num - 1) // 10 + 1
        counts[decade] = counts.get(decade, 0) + 1

        if decade not in first_seen:
            first_seen[decade] = index

    best_decade = None
    best_count = -1
    best_first_seen = 999

    for decade, count in counts.items():
        if count > best_count or (count == best_count and first_seen[decade] < best_first_seen):
            best_decade = decade
            best_count = count
            best_first_seen = first_seen[decade]

    return best_decade


def group_s(s):
    return "LOW" if 1 <= s <= 5 else "HIGH"


try:
    res = requests.get(API_URL, timeout=20)
    data = res.json()

    results = []

    for draw in data:
        if "winningNumbers" not in draw:
            continue
        if "list" not in draw["winningNumbers"]:
            continue

        numbers = draw["winningNumbers"]["list"]

        if not numbers:
            continue

        draw_id = draw["drawId"]
        draw_time = datetime.fromtimestamp(draw["drawTime"] / 1000).strftime("%H:%M")
        s_value = calculate_s_value(numbers)

        results.append({
            "draw_id": draw_id,
            "time": draw_time,
            "s": s_value,
            "group": group_s(s_value)
        })

    results = sorted(results, key=lambda x: x["draw_id"])

    print("Last S values:")
    for r in results[-5:]:
        print(r)

    if len(results) >= 5:
        last_5 = results[-5:]
        groups = [r["group"] for r in last_5]

        if all(g == "LOW" for g in groups):
            send_message("Teleperformance LOW")
        elif all(g == "HIGH" for g in groups):
            send_message("Teleperformance HIGH")
        else:
            print("No 5 LOW/HIGH pattern found.")
    else:
        print("Not enough completed draws.")

except Exception as e:
    print("Error:", e)
