import smtplib
from email.message import EmailMessage

from aiosmtplib import send
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


async def send_mail_async(subject, recipient_email, body) -> str:
    message = EmailMessage()
    message["From"] = "noreply@parda.af"
    message["To"] = recipient_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await send(
            message,
            hostname="localhost",
            port=25,  # or 587 if you use auth
        )
        return "email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"


async def send_mail_html(subject, recipient_email, html_content, text_content) -> str:
    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = "noreply-parda.af@parda.af"
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach both plain text and HTML versions
    text_part = MIMEText(text_content)
    html_part = MIMEText(html_content, "html")

    message.attach(text_part)
    message.attach(html_part)

    try:
        await send(
            message,
            hostname="localhost",
            port=25,  # or 587 if you use auth
            start_tls=True
        )
        return "email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

#
# async def send_mail_html(subject: str, recipient_email: str, confirmation_link: str):
#     smtp_host = "smtp.basirsoft.tech"   # your SMTP server
#     smtp_port = 587
#
#     # Load or format your HTML template
#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head><meta charset="utf-8"></head>
#     <body>
#     <h2>One last step...</h2>
#     <p>Please confirm your subscription to the <strong>Parda.af Newsletter</strong>.</p>
#     <a href="{confirmation_link}">Confirm Subscription</a>
#     </body>
#     </html>
#     """
#
#     # Create message
#     message = MIMEMultipart("alternative")
#     message["From"] = sender_email
#     message["To"] = recipient_email
#     message["Subject"] = subject
#
#     # Attach both plain text and HTML versions
#     text_part = MIMEText("Please confirm your subscription by visiting the following link: " + confirmation_link, "plain")
#     html_part = MIMEText(html_content, "html")
#
#     message.attach(text_part)
#     message.attach(html_part)
#
#     # Send using aiosmtplib
#     try:
#         await aiosmtplib.send(
#             message,
#             hostname=smtp_host,
#             port=smtp_port,
#             start_tls=True,
#             username=sender_email,
#             password=sender_password,
#         )
#         print("✅ Email sent successfully.")
#     except Exception as e:
#         print(f"❌ Error sending email: {e}")