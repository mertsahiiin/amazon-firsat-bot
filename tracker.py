import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DB_FILE = "prices.json"

SEARCHES = [
    "iPhone 17 Pro Max",
    "iPhone 17 Pro",
    "iPhone 17",
    "iPhone 16 Pro Max",
    "iPhone 16 Pro",
    "iPhone 16",
    "Apple Watch",
    "MacBook",
    "Huawei Watch Fit"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print("Telegram status:", r.status_code)
    print("Telegram response:", r.text)

def price_to_number(price_text):
    cleaned = re.sub(r"[^\d,]", "", price_text)
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except:
        return None

def load_prices():
    if not os.path.exists(DB_FILE):
        print("prices.json yok, ilk tarama.")
        return {}

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_prices(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def title_matches_query(title, query):
    t = title.lower()
    q = query.lower()

    if "iphone 17 pro max" in q:
        return "iphone 17 pro max" in t

    if "iphone 17 pro" in q:
        return "iphone 17 pro" in t and "max" not in t

    if "iphone 17" in q:
        return "iphone 17" in t and "pro" not in t

    if "iphone 16 pro max" in q:
        return "iphone 16 pro max" in t

    if "iphone 16 pro" in q:
        return "iphone 16 pro" in t and "max" not in t

    if "iphone 16" in q:
        return "iphone 16" in t and "pro" not in t

    if "apple watch" in q:
        return "apple watch" in t

    if "macbook" in q:
        return "macbook" in t

    if "huawei watch fit" in q:
        return "huawei" in t and "watch" in t and "fit" in t

    return False

old_prices = load_prices()
new_prices = dict(old_prices)
alerts = []

for query in SEARCHES:
    url = "https://www.amazon.com.tr/s?k=" + quote_plus(query)
    print("Aranıyor:", query)

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print("Amazon status:", r.status_code)

        if r.status_code != 200:
            print("Amazon sayfa vermedi:", r.status_code)
            time.sleep(3)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        products = soup.select("[data-component-type='s-search-result']")[:3]

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

            if not title_matches_query(title, query):
                print("Atlandı:", title)
                continue

            key = title.lower()[:120]

            print("Ürün:", title)
            print("Fiyat:", price_text)

            if key in old_prices:
                old_price = old_prices[key]["price"]

                if price_num < old_price:
                    discount = round(((old_price - price_num) / old_price) * 100, 1)

                    alerts.append(
                        f"🔥 Amazon fiyat düştü! %{discount}\n\n"
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

        time.sleep(3)

    except Exception as e:
        print("Hata:", query, e)

save_prices(new_prices)

if alerts:
    send_telegram("📉 Amazon Apple / Huawei indirim bildirimi\n\n" + "\n\n".join(alerts[:5]))
else:
    print("Yeni indirim yok, mesaj gönderilmedi.")

print("Tamamlandi")
