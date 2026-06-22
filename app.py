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
    decades = set()
    for num in numbers:
        decades.add((num - 1) // 10 + 1)
    return len(decades)


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
    for r in results[-8:]:
        print(r)

    if len(results) >= 7:
        before_pattern = results[-7]
        last_5 = results[-6:-1]
        sixth = results[-1]

        groups = [r["group"] for r in last_5]

        if all(g == "LOW" for g in groups) or all(g == "HIGH" for g in groups):
            pattern_group = groups[0]

            # Αυτό κόβει τα επαναλαμβανόμενα alerts.
            # Στέλνει μόνο όταν το σερί των 5 μόλις δημιουργήθηκε.
            if before_pattern["group"] != pattern_group:
                message = (
                    "🚨 KINO ALERT\n\n"
                    f"5 συνεχόμενα {pattern_group}\n\n"
                    f"1) {last_5[0]['time']} → Σ {last_5[0]['s']}\n"
                    f"2) {last_5[1]['time']} → Σ {last_5[1]['s']}\n"
                    f"3) {last_5[2]['time']} → Σ {last_5[2]['s']}\n"
                    f"4) {last_5[3]['time']} → Σ {last_5[3]['s']}\n"
                    f"5) {last_5[4]['time']} → Σ {last_5[4]['s']}\n\n"
                    f"6ο:\n"
                    f"{sixth['time']} → Σ {sixth['s']} ({sixth['group']})"
                )

                send_message(message)
            else:
                print("Pattern continues. Alert already sent before.")
        else:
            print("No 5 LOW/HIGH pattern found.")
    else:
        print("Not enough completed draws.")

except Exception as e:
    print("Error:", e)
