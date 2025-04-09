import smtplib

from aiosmtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(subject, recipient_email, body):
    # SMTP server configuration
    smtp_server = "smtp.mailgun.org"
    smtp_port = 587
    sender_email = "noreply@parda.af"
    sender_password = "afc6e1d2c40ed5202c114de70fc8a983-3af52e3b-10f63034"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        server.quit()


# async def send_mail_async(subject, recipient_email, body):
#     smtp_host = "smtp.mailgun.org"
#     smtp_port = 587
#     sender_email = "parda.af-noreply@parda.af"
#     sender_password = "afc6e1d2c40ed5202c114de70fc8a983-3af52e3b-10f63034"
#
#     msg = EmailMessage
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = recipient_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))
#
#     smtp = SMTP(hostname=smtp_host, port=smtp_port, start_tls=True)
#
#     try:
#         await smtp.connect()
#         await smtp.login(sender_email, sender_password)
#         await smtp.send_message(msg)
#         print("Email sent successfully!")
#     except Exception as e:
#         print(f"Error sending email: {e}")
#     finally:
#         if smtp.is_connected:
#             await smtp.quit()


async def send_mail_async(subject: str, recipient_email: str, body: str):
    smtp_host = "smtp.mailgun.org"
    smtp_port = 587
    sender_email = "parda.af-noreply@parda.af"
    sender_password = "afc6e1d2c40ed5202c11af52e3b-10f63034"

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # Create SMTP client
    smtp = SMTP(
        hostname=smtp_host,
        port=smtp_port,
        start_tls=True,  # Use STARTTLS
        timeout=10  # Add timeout for operations
    )

    try:
        # Connect and send
        await smtp.connect()
        await smtp.login(sender_email, sender_password)
        await smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise  # Re-raise the exception if you want calling code to handle it
    finally:
        if smtp.is_connected:
            await smtp.quit()
