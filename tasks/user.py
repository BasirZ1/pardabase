import asyncio

from celery_app import celery_app
from db import get_emails_high_clearance_users_ps, get_all_gallery_db_names
from db.earning import calculate_all_due_salaries_with_report_ps
from helpers import send_salary_report_email
from utils import set_current_db, flatbed


@celery_app.task
def scheduled_salary_calculations_with_email():
    """
    Scheduled task that calculates all due salaries for all tenants
    and reports to their owners/managers.
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

                    result = await calculate_all_due_salaries_with_report_ps()

                    if not result:
                        await flatbed("warning", f"No results returned from calculate_all_due_salaries_with_report_ps")
                        continue

                    processed = result.get("processed", 0)
                    errors = result.get("errors", 0)
                    total_amount = result.get("total_amount", 0)
                    summary = result.get("summary", "")

                    # ✅ Only send email if there's something to report
                    if processed > 0 or errors > 0:
                        recipients = await get_emails_high_clearance_users_ps()
                        await send_salary_report_email(
                            processed, errors, total_amount, summary, recipients
                        )
                    else:
                        await flatbed("info", f"Skipping calculation email, nothing to report")

                except Exception as tenant_error:
                    await flatbed("exception", f"In celery salary_calculations_with_email: {tenant_error}")
                    continue  # move to next tenant

        except Exception as e:
            set_current_db("pardaaf_main")
            await flatbed("exception", f"In celery salary_calculations_with_email: {e}")
            return {"status": "error", "error": str(e)}

    # =====================
    # ✅ Celery + asyncio integration
    # =====================
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # In Celery, loop is usually not running → safe to just run until complete
    return loop.run_until_complete(run_for_all_tenants())
