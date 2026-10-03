import os

BOT_TOKEN = "8827586234:AAGlQGfyMpujK-HLdt6312dH6tfI-sNP25Y"
ADMIN_IDS = [7869546163]  # Shu yerga o'zingizning Telegram ID'ingizni yozing

DB_NAME = "flower_shop.db"

FLOWERS_CATALOG = {
    "Petuniya": {
        "price": 2000,
        "colors": ["Qizil", "Oq", "Siyohrang", "Pushti"],
        "description": "Chiroyli bezak guli, parvarishi oson."
    },
    "Chinni gul": {
        "price": 3000,
        "colors": ["Qizil", "Oq", "Sariq", "Pushti"],
        "description": "Xushbo'y va uzoq saqlanuvchi gul."
    },
    "Atir gul": {
        "price": 15000,
        "colors": ["Qizil", "Oq", "Sariq", "Pushti"],
        "description": "Klassik go'zallik va oliy navli atirgul."
    },
    "Lola": {
        "price": 8000,
        "colors": ["Qizil", "Sariq", "Oq"],
        "description": "Bahoriy va nafis gul."
    },
	[03.10.2026 20:52] Sherxon: [ keyboards.py ]
[03.10.2026 21:59] Sherxon: import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Render uchun soxta veb-server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Serverni orqa fonda ishga tushirish
threading.Thread(target=run_web_server, daemon=True).start()
    "Kaktus": {
        "price": 12000,
        "colors": ["Yashil"],
        "description": "Xona uchun va parvarish talab qilmaydigan o'simlik."
    }
}
	



