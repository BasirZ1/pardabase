import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv(override=True)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def send_notification(chat_id: int, text: str):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)
    await bot.session.close()
