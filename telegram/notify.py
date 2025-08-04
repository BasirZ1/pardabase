import os

from aiogram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PRIVATE_KEY_PATH = "private.key"


async def send_notification(chat_id: int, text: str):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)
    await bot.session.close()
