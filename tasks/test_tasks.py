import asyncio

from celery_app import celery_app

from utils import send_mail
from utils.config import ADMIN_EMAIL


# Scheduled task
@celery_app.task
def scheduled_hello():
    asyncio.run(send_mail(
        subject="Scheduled HELLO",
        recipient_email=ADMIN_EMAIL,
        body="Celery worker says Hello"
    ))


# Delayed / async task
@celery_app.task
def delayed_hello(message):
    asyncio.run(send_mail(
        subject="Delayed HELLO",
        recipient_email=ADMIN_EMAIL,
        body=f"Celery worker says Hello {message}"
    ))
