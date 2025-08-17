from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "curtains_tasks",
    broker="redis://localhost:6379/1"
)
celery_app.conf.timezone = "Kabul/Asia"


# Periodic scheduled task
celery_app.conf.beat_schedule = {
    "send_scheduled_hello": {
        "task": "tasks.test_tasks.scheduled_hello",
        "schedule": crontab(hour=15, minute=0),  # fires daily at 15:00 Kabul time
        "args": (),  # no arguments
    }
}