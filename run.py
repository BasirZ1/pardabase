import asyncio

from db import get_notifications_for_user_ps
from utils import set_current_db


async def run_this():
    set_current_db("zmt")
    data = await get_notifications_for_user_ps('0bc3e678-00d4-4ed2-8901-dbaa79a86c4e', 1, None)
    print(data)

asyncio.run(run_this())
