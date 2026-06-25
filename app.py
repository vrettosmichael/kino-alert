import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

GAME_ID = 1100
STATE_FILE = "/opt/kino-alert/last_alert.txt"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": text},
        timeout=15
    )
    print(response.status_code)
    print(response.text)
    response.raise_for_status()


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
    if 1 <= s <= 5:
        return "LOW"
    if 6 <= s <= 10:
        return "HIGH"
    return "UNKNOWN"


def get_last_completed_draw_id():
    url = f"https://api.opap.gr/draws/v3.0/{GAME_ID}/last-result-and-active"
    data = requests.get(url, timeout=15).json()
    return data["last"]["drawId"]


def get_draw(draw_id):
    url = f"https://api.opap.gr/draws/v3.0/{GAME_ID}/{draw_id}"
    return requests.get(url, timeout=15).json()


def read_last_alert():
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def write_last_alert(alert_key):
    with open(STATE_FILE, "w") as f:
        f.write(alert_key)


try:
    last_draw_id = get_last_completed_draw_id()

    results = []

    for draw_id in range(last_draw_id - 4, last_draw_id + 1):
        draw = get_draw(draw_id)

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
        current_draw_id = results[-1]["drawId"]

        alert_text = None

        if all(g == "LOW" for g in groups):
            alert_text = "Teleperformance LOW"
        elif all(g == "HIGH" for g in groups):
            alert_text = "Teleperformance HIGH"

        if alert_text:
            alert_key = f"{alert_text}:{current_draw_id}"
            last_alert = read_last_alert()

            if alert_key != last_alert:
                send_message(alert_text)
                write_last_alert(alert_key)
                print(f"Alert sent: {alert_key}")
            else:
                print(f"Duplicate alert skipped: {alert_key}")
        else:
            print("No alert")
    else:
        print("Could not read 5 completed draws")

except Exception as e:
    print("ERROR:", e)
