from celery_app import celery_app
from utils import cleanup_old_backups


@celery_app.task
def scheduled_cleanup_all_backups():
    cleanup_old_backups("daily")


@celery_app.task
def scheduled_cleanup_all_backups_weekly():
    cleanup_old_backups("weekly")


@celery_app.task
def scheduled_cleanup_all_backups_monthly():
    cleanup_old_backups("monthly")
