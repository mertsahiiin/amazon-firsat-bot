import os
import requests
from urllib.parse import quote_plus

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

queries = [
    "Apple AirPods",
    "Apple Watch",
    "Apple iPad",
    "Apple MacBook",
    "Apple iPhone",
    "Apple Pencil",
    "Apple şarj adaptörü",
    "Apple MagSafe",
]

message = "🍎 Amazon Türkiye Apple indirim takip linkleri:\n\n"

for q in queries:
    url = "https://www.amazon.com.tr/s?k=" + quote_plus(q)
    message += f"🔎 {q}\n{url}\n\n"

api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
response = requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

print("Status:", response.status_code)
print("Response:", response.text)
