import asyncio

from db import update_user
from utils import set_current_db


async def update_users():
    set_current_db("rifa_db_4011")
    await update_user("basirzurmati", "Basir Zurmati",
                      "basirzurmati", 5, "@Basir7233$")


asyncio.run(update_users())
