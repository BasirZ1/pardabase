from email.utils import formataddr

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


async def send_mail(subject, recipient_email, body) -> str:
    """
    Send a plain text or HTML email asynchronously.
    :param subject: The subject of the email
    :param recipient_email: The recipient's email address
    :param body: The email body (plain text or HTML)
    :return: Success or error message
    """
    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = formataddr(("parda.af", "noreply@parda.af"))
    message["To"] = recipient_email
    message["Subject"] = subject

    text_part = MIMEText(body)
    message.attach(text_part)

    try:
        # Send email asynchronously using aiosmtplib
        async with aiosmtplib.SMTP(hostname="localhost", port=25, start_tls=False) as server:
            await server.send_message(message)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"


async def send_mail_html(subject, recipient_email, html_content, text_content) -> str:
    """
    Send an HTML email with both plain text and HTML content.
    :param subject: The subject of the email
    :param recipient_email: The recipient's email address
    :param html_content: The HTML body of the email
    :param text_content: The plain text body of the email
    :return: Success or error message
    """
    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = formataddr(("parda.af", "noreply@parda.af"))
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach both plain text and HTML versions
    text_part = MIMEText(text_content)
    html_part = MIMEText(html_content, "html")

    message.attach(text_part)
    message.attach(html_part)

    try:
        # Send email asynchronously using aiosmtplib
        async with aiosmtplib.SMTP(hostname="localhost", port=25, start_tls=False) as server:
            await server.send_message(message)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"
