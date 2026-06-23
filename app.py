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

def calculate_s(numbers):
    counts = {}

    for num in numbers:
        decade = (num - 1) // 10 + 1

        if decade not in counts:
            counts[decade] = 0

        counts[decade] += 1

    max_count = max(counts.values())

    for decade in range(1, 9):
        if counts.get(decade, 0) == max_count:
            return decade

try:

    latest = requests.get(
        "https://api.opap.gr/draws/v3.0/1100/last-result-and-active",
        timeout=10
    ).json()

    last_draw_id = latest["last"]["drawId"]

    from_draw = last_draw_id - 4
    to_draw = last_draw_id

    draws = requests.get(
        f"https://api.opap.gr/draws/v3.0/1100/draw-date/{from_draw}/{to_draw}",
        timeout=10
    ).json()

    results = []

    for draw in draws:

        if "winningNumbers" not in draw:
            continue

        numbers = draw["winningNumbers"]["list"]

        s = calculate_s(numbers)

        group = "LOW" if s <= 5 else "HIGH"

        results.append({
            "drawId": draw["drawId"],
            "s": s,
            "group": group
        })

    results = sorted(results, key=lambda x: x["drawId"])

    print("Last 5 draws:")
    for r in results:
        print(r)

    if len(results) == 5:

        groups = [r["group"] for r in results]

        if all(g == "HIGH" for g in groups):
            send_message("Teleperformance HIGH")
            print("HIGH alert sent")

        elif all(g == "LOW" for g in groups):
            send_message("Teleperformance LOW")
            print("LOW alert sent")

        else:
            print("No alert")

except Exception as e:
    print("ERROR:", e)
