import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEARCHES = [
    "Apple AirPods",
    "Apple Watch",
    "Apple iPhone",
    "Huawei Watch",
    "Huawei telefon",
    "Huawei FreeBuds"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

found = []

for query in SEARCHES:
    url = "https://www.amazon.com.tr/s?k=" + quote_plus(query)

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)

        soup = BeautifulSoup(r.text, "html.parser")

        products = soup.select(
            "[data-component-type='s-search-result']"
        )[:3]

        for p in products:

            title_el = p.select_one("h2 span")
            price_el = p.select_one(".a-price .a-offscreen")

            if not title_el:
                continue

            title = title_el.get_text(strip=True)

            if price_el:
                price = price_el.get_text(strip=True)
            else:
                price = "Fiyat bulunamadı"

            found.append(
                f"📦 {title}\n💰 {price}"
            )

    except Exception as e:
        found.append(f"Hata: {query}")

if found:
    message = "🍎 Apple / Huawei Kontrol\n\n"
    message += "\n\n".join(found[:10])
else:
    message = "Ürün bulunamadı."

send_telegram(message)

print("Tamamlandı")
