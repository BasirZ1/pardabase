from celery_app import celery_app
from db import get_all_gallery_db_names, check_due_add_notification_for_related_staff
from helpers import run_async
from utils import set_current_db, flatbed


@celery_app.task
def scheduled_notify_salesman_tailor():
    """
    Scheduled task that checks due bills and notifies related salesmen and tailors.
    """

    async def run_for_all_tenants():
        try:
            # Step 1: Always start with main db
            set_current_db("pardaaf_main")

            # Step 2: Fetch all gallery db_names
            db_names = await get_all_gallery_db_names()

            for db_name in db_names:
                try:
                    # Step 3: Switch to each tenant DB
                    set_current_db(db_name)

                    result = await check_due_add_notification_for_related_staff()

                except Exception as tenant_error:
                    await flatbed("exception", f"In celery notify_salesman_tailor: {tenant_error}")
                    continue  # move to next tenant

        except Exception as e:
            set_current_db("pardaaf_main")
            await flatbed("exception", f"In celery notify_salesman_tailor: {e}")
            return {"status": "error", "error": str(e)}

    run_async(run_for_all_tenants())
