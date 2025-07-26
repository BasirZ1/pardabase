import asyncio

from db import get_drafts_list_ps, get_cutting_history_list_ps, insert_new_purchase, insert_new_supplier, \
    update_supplier, get_supplier_ps, get_suppliers_list_ps, remove_supplier_ps
from utils import set_current_db


async def run_this():
    set_current_db("zmt")

    await remove_supplier_ps(1)
    suppliers = await get_suppliers_list_ps()
    print(suppliers)
    # await get_recent_activities_preview()
    # # await update_user("basirzurmati", "Basir Zurmati",
    # #                   "basirzurmati", 5, "@Basir7233$")


asyncio.run(run_this())
