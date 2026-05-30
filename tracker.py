import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DB_FILE = "prices.json"

SEARCHES = [
    "iPhone 17 Pro Max 256GB",
    "iPhone 17 Pro Max 512GB",
    "iPhone 17 Pro Max 1TB",
    "iPhone 17 Pro 256GB",
    "iPhone 17 Pro 512GB",
    "iPhone 17 Pro 1TB",
    "iPhone 17 256GB",
    "iPhone 17 512GB",
    "iPhone 17 1TB",

    "iPhone 16 Pro Max 256GB",
    "iPhone 16 Pro Max 512GB",
    "iPhone 16 Pro Max 1TB",
    "iPhone 16 Pro 256GB",
    "iPhone 16 Pro 512GB",
    "iPhone 16 Pro 1TB",
    "iPhone 16 256GB",
    "iPhone 16 512GB",
    "iPhone 16 1TB",

    "Apple MacBook",
    "Apple Watch Series",
    "Huawei Watch Fit 5 Pro",
    "Huawei Watch Fit 4 Pro",
    "Huawei Watch Fit 5",
    "Huawei Watch Fit 4"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print("Telegram status:", r.status_code)
    print("Telegram response:", r.text)

def price_to_number(text):
    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})", text)
    if not match:
        return None
    return float(match.group(1).replace(".", "").replace(",", "."))

def load_prices():
    if not os.path.exists(DB_FILE):
        print("prices.json yok, ilk tarama.")
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
    url = "https://www.epey.com/arama?q=" + quote_plus(query)
    print("Aranıyor:", query)

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print("Epey status:", r.status_code)

        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select("li, div, article")[:500]
        found_count = 0

        for item in items:
            text = item.get_text(" ", strip=True)

            if "TL" not in text:
                continue

            low = text.lower()
            if "apple" not in low and "huawei" not in low:
                continue

            price_num = price_to_number(text)
            if price_num is None:
                continue

            link_el = item.select_one("a[href]")
            if not link_el:
                continue

            title = link_el.get_text(" ", strip=True)
            if len(title) < 8:
                title = text[:120]

            link = urljoin("https://www.epey.com", link_el.get("href"))
            key = title[:100]

            found_count += 1

            print("Ürün:", title)
            print("Fiyat:", price_num)

            if key in old_prices:
                old_price = old_prices[key]["price"]

                if price_num < old_price:
                    discount = round(((old_price - price_num) / old_price) * 100, 1)

                    alerts.append(
                        f"🔥 Fiyat düştü! %{discount}\n\n"
                        f"📦 {title}\n"
                        f"Eski fiyat: {old_prices[key]['price_text']}\n"
                        f"Yeni fiyat: {price_num:,.2f} TL\n"
                        f"🔗 {link}"
                    )

            new_prices[key] = {
                "title": title,
                "price": price_num,
                "price_text": f"{price_num:,.2f} TL",
                "link": link
            }

            if found_count >= 5:
                break

        print(query, "bulunan ürün:", found_count)

    except Exception as e:
        print("Hata:", query, e)

save_prices(new_prices)

if alerts:
    send_telegram("📉 Epey Apple / Huawei indirim bildirimi\n\n" + "\n\n".join(alerts[:5]))
else:
    print("Yeni indirim yok, mesaj gönderilmedi.")

print("Tamamlandi")
