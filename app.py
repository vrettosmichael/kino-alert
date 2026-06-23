import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

GAME_ID = 1100


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print(response.status_code)
    print(response.text)


def calculate_s(numbers):
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
        if count > best_count:
            best_decade = decade
            best_count = count
            best_first_seen = first_seen[decade]
        elif count == best_count and first_seen[decade] < best_first_seen:
            best_decade = decade
            best_first_seen = first_seen[decade]

    return best_decade


def group_s(s):
    return "LOW" if s <= 5 else "HIGH"


try:
    latest_url = f"https://api.opap.gr/draws/v3.0/{GAME_ID}/last-result-and-active"
    latest_data = requests.get(latest_url, timeout=15).json()

    last_draw_id = latest_data["last"]["drawId"]

    results = []

    for draw_id in range(last_draw_id - 4, last_draw_id + 1):
        draw_url = f"https://api.opap.gr/draws/v3.0/{GAME_ID}/{draw_id}"
        draw = requests.get(draw_url, timeout=15).json()

        if "winningNumbers" not in draw:
            print(f"Missing winningNumbers for draw {draw_id}")
            continue

        numbers = draw["winningNumbers"]["list"]

        s = calculate_s(numbers)
        group = group_s(s)

        results.append({
            "drawId": draw_id,
            "s": s,
            "group": group
        })

    print("Last 5 draws:")
    for r in results:
        print(r)

    if len(results) == 5:
        groups = [r["group"] for r in results]

        if all(g == "LOW" for g in groups):
            send_message("Teleperformance LOW")
        elif all(g == "HIGH" for g in groups):
            send_message("Teleperformance HIGH")
        else:
            print("No alert")
    else:
        print("Could not read 5 completed draws")

except Exception as e:
    print("ERROR:", e)
