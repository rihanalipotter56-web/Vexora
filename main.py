import os
from dotenv import load_dotenv

from core.bot import VexoraBot
from core.database import setup_database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

setup_database()

bot = VexoraBot()

bot.run(TOKEN)
