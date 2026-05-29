import os
import requests
from urllib.parse import quote_plus

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

queries = [
    "Amazon Depo Apple iPhone",
    "Amazon Depo Apple Watch",
    "Amazon Depo Apple AirPods",
    "Amazon Depo Apple iPad",
    "Amazon Depo Apple MacBook",
]

message = "🍎 Amazon Depo Apple takip linkleri:\n\n"

 for_query = []
for q in queries:
    url = "https://www.amazon.com.tr/s?k=" + quote_plus(q)
    message += f"🔎 {q}\n{url}\n\n"

api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
response = requests.post(api_url, data={"chat_id": CHAT_ID, "text": message})

print("Status:", response.status_code)
print("Response:", response.text)
