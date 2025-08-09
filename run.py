import asyncio

from db import get_supplier_ps
from utils import set_current_db


async def run_this():
    set_current_db("zmt")
    data = await get_supplier_ps(4)
    print(data)
    # await get_recent_activities_preview()
    # # await update_user("basirzurmati", "Basir Zurmati",
    # #                   "basirzurmati", 5, "@Basir7233$")


asyncio.run(run_this())
