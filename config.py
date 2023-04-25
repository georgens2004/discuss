import os
from dotenv import load_dotenv

load_dotenv()

''' TOP SECRET '''

# Telegram bot config

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
ADMIN_TG_ID = os.getenv("ADMIN_TG_ID")

# Database

HOST = os.getenv('HOST')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_DATABASE = os.getenv('PG_DATABASE')

