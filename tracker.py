import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DB_FILE = "prices.json"

SEARCHES = [
    "Apple AirPods",
    "Apple Watch",
    "Apple iPhone",
    "Apple iPad",
    "Apple MacBook",
    "Huawei Watch",
    "Huawei telefon",
    "Huawei tablet",
    "Huawei FreeBuds"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)

def price_to_number(price_text):
    cleaned = re.sub(r"[^\d,]", "", price_text)
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except:
        return None

def load_prices():
    if not os.path.exists(DB_FILE):
        print("prices.json yok, ilk tarama yapılacak.")
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_prices(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

old_prices = load_prices()
new_prices = dict(old_prices)
alerts = []

for query in SEARCHES:
    url = "https://www.amazon.com.tr/s?k=" + quote_plus(query)
    print("Aranıyor:", query)

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print("Amazon status:", r.status_code)

        soup = BeautifulSoup(r.text, "html.parser")
        products = soup.select("[data-component-type='s-search-result']")[:5]

        print(query, "ürün sayısı:", len(products))

        for p in products:
            title_el = p.select_one("h2 span")
            price_el = p.select_one(".a-price .a-offscreen")
            link_el = p.select_one("h2 a")

            if not title_el or not price_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            price_text = price_el.get_text(strip=True)
            price_num = price_to_number(price_text)
            link = "https://www.amazon.com.tr" + link_el.get("href")

            if price_num is None:
                continue

            key = title[:100]

            print("Ürün:", title)
            print("Fiyat:", price_text)

            if key in old_prices:
                old_price = old_prices[key]["price"]

                if price_num < old_price:
                    discount = round(((old_price - price_num) / old_price) * 100, 1)

                    alerts.append(
                        f"🔥 Fiyat düştü! %{discount}\n\n"
                        f"📦 {title}\n"
                        f"Eski fiyat: {old_prices[key]['price_text']}\n"
                        f"Yeni fiyat: {price_text}\n"
                        f"🔗 {link}"
                    )

            new_prices[key] = {
                "title": title,
                "price": price_num,
                "price_text": price_text,
                "link": link
            }

    except Exception as e:
        print("Hata:", query, e)

save_prices(new_prices)

if alerts:
    send_telegram("📉 Apple / Huawei indirim bildirimi\n\n" + "\n\n".join(alerts[:5]))
else:
    print("Yeni indirim yok, mesaj gönderilmedi.")

print("Tamamlandi")
