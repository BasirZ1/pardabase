from zoneinfo import ZoneInfo

from celery_app import celery_app
from db import get_all_gallery_db_names
from helpers import run_async
from utils import set_current_db, flatbed, backup_to_gdrive

import subprocess
import os
from datetime import datetime


@celery_app.task
def scheduled_backup_all_tenants():
    run_async(backup_all_tenants("daily"))


@celery_app.task
def scheduled_backup_all_tenants_weekly():
    run_async(backup_all_tenants("weekly"))


@celery_app.task
def scheduled_backup_all_tenants_monthly():
    run_async(backup_all_tenants("monthly"))


@celery_app.task
def scheduled_backup_all_tenants_yearly():
    run_async(backup_all_tenants("yearly"))


async def backup_all_tenants(period: str):
    main_db = "pardaaf_main"
    set_current_db(main_db)
    kabul_tz = ZoneInfo("Asia/Kabul")
    timestamp = datetime.now(kabul_tz).strftime('%Y%m%d_%H%M%S')

    await backup_single_db(main_db, timestamp, period)

    db_names = await get_all_gallery_db_names()
    for db_name in db_names:
        try:
            await backup_single_db(db_name, timestamp, period)
        except Exception as tenant_error:
            await flatbed("exception", f"In celery backup {db_name}: {tenant_error}")
            continue


async def backup_single_db(db_name: str, timestamp: str, period: str = "daily"):
    """
    Dump a single DB in custom (.dump) format and push to Google Drive via rclone.
    period = daily | weekly | monthly
    """
    dump_file = f"/tmp/{db_name}_{timestamp}.dump"

    # Use pg_dump with custom format (-Fc)
    cmd = [
        "/usr/bin/pg_dump",
        "-h", os.getenv("DB_HOST", "localhost"),
        "-U", os.getenv("DB_USER", "postgres"),
        "-Fc",  # custom format (compressed)
        "-d", db_name,
        "-f", dump_file,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("DB_PASSWORD", "")

    try:
        subprocess.run(cmd, check=True, env=env)

        # Upload
        backup_to_gdrive(dump_file, period, db_name)

        await flatbed("info", f"Backup uploaded for {db_name} {period} → {dump_file}")

    except Exception as e:
        await flatbed("exception", f"Backup failed for {db_name}: {e}")
        raise
    finally:
        # Always try to remove the dump, even if upload fails
        if os.path.exists(dump_file):
            os.remove(dump_file)
