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
    'daily-salary-calculation': {
        'task': 'tasks.user.scheduled_salary_calculations_with_email',
        'schedule': crontab(minute=10),  # Run daily at 11:30 PM
    }
}

celery_app.autodiscover_tasks(["tasks"])
