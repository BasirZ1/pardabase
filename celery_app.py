import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv(override=True)
redis_url = os.getenv("RED_URL")

celery_app = Celery(
    "curtains_tasks",
    broker=f"{redis_url}/1"
)
celery_app.conf.timezone = "Asia/Kabul"


# Periodic scheduled task
celery_app.conf.beat_schedule = {
    "send_scheduled_hello": {
        "task": "tasks.test_tasks.scheduled_hello",
        "schedule": crontab(hour=15, minute=0),  # fires daily at 15:00 Kabul time
        "args": (),  # no arguments
    }
}

celery_app.autodiscover_tasks(["tasks"])
