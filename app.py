import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

try:
    url = "https://www.kinox.gr/kliroseis-kino"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    # βρίσκουμε το πρώτο αποτέλεσμα (τελευταία κλήρωση)
    result = soup.find("div", class_="kino-result")

    # βρίσκουμε το Σ (συνήθως είναι μέσα σε span)
    s_value = result.find("span", class_="sum").text.strip()

    print("S value:", s_value)

    s_value = int(s_value)

    if s_value == 3 or s_value == 4:
        send_message(f"🎯 KINO ALERT\nΣειρά: {s_value}")

except Exception as e:
    print("Error:", e)
