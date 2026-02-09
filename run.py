import asyncio

from db import get_fx_current_rate
from tasks.exchange import fetch_current_rates_and_update_db
from utils import set_current_db


async def run_this():
    set_current_db("pardaaf_main")
    data = await get_fx_current_rate("AFN")
    print(data)
    # data = await get_notifications_for_user_ps('0bc3e678-00d4-4ed2-8901-dbaa79a86c4e', 1, None)


asyncio.run(run_this())
