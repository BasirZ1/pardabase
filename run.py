import asyncio

from db import get_supplier_ps, report_tags_list
from db.earning import calculate_all_due_salaries_with_report_ps
from utils import set_current_db


async def run_this():
    set_current_db("zmt")
    data = await calculate_all_due_salaries_with_report_ps()
    print(data)
    # await get_recent_activities_preview()
    # # await update_user("basirzurmati", "Basir Zurmati",
    # #                   "basirzurmati", 5, "@Basir7233$")


asyncio.run(run_this())
