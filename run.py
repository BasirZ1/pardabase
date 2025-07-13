import asyncio

from db import get_drafts_list_ps
from utils import set_current_db


async def update_users():
    set_current_db("zmt")
    drafts = await get_drafts_list_ps()
    print(drafts)
    # await get_recent_activities_preview()
    # # await update_user("basirzurmati", "Basir Zurmati",
    # #                   "basirzurmati", 5, "@Basir7233$")


asyncio.run(update_users())


