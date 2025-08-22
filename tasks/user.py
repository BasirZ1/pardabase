import asyncio

from celery_app import celery_app
from db import get_emails_high_clearance_users_ps
from db.earning import calculate_all_due_salaries_with_report_ps
from helpers import send_salary_report_email
from utils import set_current_db, flatbed


@celery_app.task
def scheduled_salary_calculations_with_email():
    """
    Scheduled task that calculates all due salaries and reports to owners and manager.
    """
    set_current_db("zmt")
    try:

        asyncio.run(flatbed("debug", "Schedule is working"))
        # Run async function in sync Celery task
        result = asyncio.run(calculate_all_due_salaries_with_report_ps())

        if result:
            # Unpack by column names
            processed = result.get("processed")
            errors = result.get("errors")
            total_amount = result.get("total_amount")
            summary = result.get("summary")

            recipients = asyncio.run(get_emails_high_clearance_users_ps())

            # Send success email
            asyncio.run(send_salary_report_email(processed, errors, total_amount, summary, recipients))

            return {
                "status": "success",
                "processed": processed,
                "errors": errors,
                "totalAmount": total_amount,
                "summary": summary,
            }
        else:
            raise Exception("No results returned from salary calculation function")

    except Exception as e:
        asyncio.run(flatbed("exception", f"In celery salary_calculations_with_email: {e}"))
        return {
            "status": "error",
            "error": str(e),
        }
