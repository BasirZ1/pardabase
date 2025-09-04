import asyncio

from db import get_notifications_for_user_ps
from helpers.format_list import make_camel_dict
from utils import set_current_db


async def run_this():
    set_current_db("zmt")
    data = {
        "product_code": "P001",
        "roll_code": "R101",
        "quantity_in_cm": 500,
        "image_url": "http://example.com/img.png",
        "cost_per_metre": 200,
        "archived": True,
    }
    print(data)
    print(make_camel_dict(data))

    # data = await get_notifications_for_user_ps('0bc3e678-00d4-4ed2-8901-dbaa79a86c4e', 1, None)


asyncio.run(run_this())
