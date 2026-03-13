# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
GOOGLE_SHEETS_URL = os.getenv("GOOGLE_SHEETS_URL")

# Безопасное преобразование ADMIN_IDS
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
if admin_ids_str:
    for part in admin_ids_str.split(","):
        part = part.strip()
        if part.isdigit():
            ADMIN_IDS.append(int(part))

print("ADMIN_IDS loaded:", ADMIN_IDS)
HOT_THRESHOLD = int(os.getenv("HOT_THRESHOLD", 12))
