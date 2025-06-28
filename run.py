import asyncio

from db import update_user, get_recent_activities_preview
from utils import set_current_db


async def update_users():
    set_current_db("rifa_db_9000")
    await get_recent_activities_preview()
    # await update_user("basirzurmati", "Basir Zurmati",
    #                   "basirzurmati", 5, "@Basir7233$")


asyncio.run(update_users())


