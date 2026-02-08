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
        'schedule': crontab(hour=19, minute=0),  # Run daily at 7:00 PM
    },
    'daily-notify-salesman-tailor': {
        'task': 'tasks.user.scheduled_notify_salesman_tailor',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9:00 AM
    },
    'daily-backup-all-tenants': {
        'task': 'tasks.backup.scheduled_backup_all_tenants',
        'schedule': crontab(hour=0, minute=0),  # midnight
    },
    'weekly-backup-all-tenants': {
        'task': 'tasks.backup.scheduled_backup_all_tenants_weekly',
        'schedule': crontab(hour=0, minute=10, day_of_week="friday"),
    },
    'monthly-backup-all-tenants': {
        'task': 'tasks.backup.scheduled_backup_all_tenants_monthly',
        'schedule': crontab(hour=0, minute=20, day_of_month="1"),
    },
    'yearly-backup-all-tenants': {
        'task': 'tasks.backup.scheduled_backup_all_tenants_yearly',
        'schedule': crontab(hour=0, minute=30, day_of_month="1", month_of_year="1"),  # Jan 1st midnight
    },
    'daily-cleanup-all-backups': {
        'task': 'tasks.cleanup.scheduled_cleanup_all_backups',
        'schedule': crontab(hour=1, minute=0),  # midnight at 1
    },
    'weekly-cleanup-all-backups': {
        'task': 'tasks.cleanup.scheduled_cleanup_all_backups_weekly',
        'schedule': crontab(hour=1, minute=10, day_of_week="friday"),
    },
    'monthly-cleanup-all-backups': {
        'task': 'tasks.cleanup.scheduled_cleanup_all_backups_monthly',
        'schedule': crontab(hour=1, minute=20, day_of_month="1", month_of_year="1"),  # Jan 1st 1AM
    },
    'fetch-current_rates': {
        'task': 'tasks.exchange.scheduled_fetch_current_rates',
        'schedule': crontab(minute=48),
    }
}

celery_app.autodiscover_tasks(["tasks"])
