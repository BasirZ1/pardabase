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
                        await flatbed("warning", f"No results for {db_name}")
                        return

                    processed = result.get("processed")
                    errors = result.get("errors")
                    total_amount = result.get("total_amount")
                    summary = result.get("summary")

                    recipients = await get_emails_high_clearance_users_ps()

                    # Step 4: Send tenant-specific email
                    await send_salary_report_email(
                        processed, errors, total_amount, summary, recipients
                    )

                except Exception as tenant_error:
                    raise tenant_error

        except Exception as e:
            set_current_db("pardaaf_main")
            await flatbed("exception", f"In celery salary_calculations_with_email: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    asyncio.run(run_for_all_tenants())
