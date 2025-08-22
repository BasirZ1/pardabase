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
    try:
        # Step 1: Always start with main db
        set_current_db("pardaaf_main")

        # Step 2: Fetch all gallery db_names
        db_names = asyncio.run(get_all_gallery_db_names())

        overall_summary = []

        for db_name in db_names:
            try:
                # Step 3: Switch to each tenant DB
                set_current_db(db_name)

                asyncio.run(flatbed("debug", f"Running salary calc for {db_name}"))

                result = asyncio.run(calculate_all_due_salaries_with_report_ps())

                if not result:
                    asyncio.run(flatbed("warning", f"No results for {db_name}"))
                    continue

                processed = result.get("processed")
                errors = result.get("errors")
                total_amount = result.get("total_amount")
                summary = result.get("summary")

                recipients = asyncio.run(get_emails_high_clearance_users_ps())

                # Step 4: Send tenant-specific email
                asyncio.run(send_salary_report_email(
                    processed, errors, total_amount, summary, recipients
                ))

                overall_summary.append({
                    "db": db_name,
                    "status": "success",
                    "processed": processed,
                    "errors": errors,
                    "totalAmount": total_amount,
                    "summary": summary,
                })

            except Exception as tenant_error:
                asyncio.run(flatbed("exception", f"Error for {db_name}: {tenant_error}"))
                overall_summary.append({
                    "db": db_name,
                    "status": "error",
                    "error": str(tenant_error),
                })

        asyncio.run(flatbed("debug", str(overall_summary)))
        return overall_summary

    except Exception as e:
        asyncio.run(flatbed("exception", f"In celery salary_calculations_with_email: {e}"))
        return {
            "status": "error",
            "error": str(e),
        }
