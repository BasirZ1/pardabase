import asyncio

from tasks.exchange import fetch_current_rates_and_update_db
from utils import set_current_db


async def run_this():
    await fetch_current_rates_and_update_db()
    # data = await get_notifications_for_user_ps('0bc3e678-00d4-4ed2-8901-dbaa79a86c4e', 1, None)


asyncio.run(run_this())
