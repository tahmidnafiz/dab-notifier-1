import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

URL = "https://www.dabbolig.dk/find-bolig/?clearParams=true"
CHECK_INTERVAL = 10  # seconds
seen_listings = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_USER_ID, "text": msg})

def fetch_listings():
    r = requests.get(URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select(".property-tile")
    listings = []
    for item in items:
        title = item.get_text(strip=True)
        link = item.get("href") or ""
        full_link = "https://www.dabbolig.dk" + link if link.startswith("/") else link
        listings.append((title, full_link))
    return listings

def monitor():
    send_telegram("🔍 Bot started. Monitoring 24/7 every 10 seconds.")
    global seen_listings
    while True:
        try:
            listings = fetch_listings()
            for title, link in listings:
                if link not in seen_listings:
                    seen_listings.add(link)
                    send_telegram(f"🏠 NEW LISTING:\n{title}\n{link}")
        except Exception as e:
            send_telegram(f"⚠️ Error: {e}")
        time.sleep(CHECK_INTERVAL)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b'Bot is running')

def start_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("", port), Handler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    start_server()
