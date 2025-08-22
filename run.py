import asyncio

from utils import set_current_db


async def run_this():
    set_current_db("zmt")

asyncio.run(run_this())
