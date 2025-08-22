import datetime
from zoneinfo import ZoneInfo

from utils import send_mail_html, flatbed


async def send_salary_report_email(processed, errors, total_amount, summary, recipients):
    """Send HTML email report"""
    try:
        kabul_tz = ZoneInfo("Asia/Kabul")
        report_date = datetime.datetime.now(kabul_tz).strftime('%Y-%m-%d')
        subject = f"Salary Calculation Report - {report_date}"

        html_summary = summary.replace('\n', '<br>')

        html_content = f"""
        <html>
        <body>
            <h2>Salary Calculation Report</h2>
            <p><strong>Date:</strong> {report_date}</p>
            <p><strong>Processed:</strong> {processed} users</p>
            <p><strong>Errors:</strong> {errors} users</p>
            <p><strong>Total Amount:</strong> {total_amount} AFN</p>
            <hr>
            <pre>{html_summary}</pre>
        </body>
        </html>
        """

        text_content = f"""
                Salary Calculation Report
                Date: {report_date}
                Processed: {processed} users
                Errors: {errors} users
                Total Amount: {total_amount} AFN
                ----------------------------------------
                {summary}
        """

        # send to multiple recipients
        for recipient in recipients:
            await send_mail_html(
                subject=subject,
                recipient_email=recipient,
                html_content=html_content,
                text_content=text_content
            )

    except Exception as e:
        await flatbed('exception', f"In send_salary_report_mail: {e}")
