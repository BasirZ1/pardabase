from telegram import send_notification
from utils.email_sender import send_mail
from utils.config import ADMIN_EMAIL, ADMIN_TELEGRAM
from utils.conn import get_connection, release_connection


# logs function
async def flatbed(prefix, message):
    await send_mail(f"{prefix}", ADMIN_EMAIL, message)
    await send_notification(ADMIN_TELEGRAM, f"{prefix}: {message}")
    conn = await get_connection()
    try:
        await conn.execute(
            "INSERT INTO log (prefix, message) VALUES ($1, $2);",
            prefix, message
        )
    finally:
        await release_connection(conn)
