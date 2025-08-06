from utils.email_sender import send_mail
from utils.config import ADMIN_EMAIL
from utils.conn import get_connection, release_connection


# logs function
async def flatbed(prefix, message):
    await send_mail(f"{prefix}", ADMIN_EMAIL, message)
    conn = await get_connection()
    try:
        await conn.execute(
            "INSERT INTO log (prefix, message) VALUES ($1, $2);",
            prefix, message
        )
    finally:
        await release_connection(conn)
