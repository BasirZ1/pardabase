from zoneinfo import ZoneInfo

from celery_app import celery_app
from db import get_all_gallery_db_names
from utils import set_current_db, flatbed, backup_to_gdrive

import asyncio
import subprocess
import os
from datetime import datetime


@celery_app.task
def scheduled_backup_all_tenants():
    """
    Scheduled task that backs up pardaaf_main + all tenant DBs and uploads to rclone.
    """

    async def run_for_all_tenants():
        try:
            kabul_tz = ZoneInfo("Asia/Kabul")
            timestamp = datetime.now(kabul_tz).strftime('%Y%m%d_%H%M%S')

            # Step 1: Always back up main db first
            main_db = "pardaaf_main"
            await backup_single_db(main_db, timestamp)

            # Step 2: Switch to main db and fetch tenant db_names
            set_current_db(main_db)
            db_names = await get_all_gallery_db_names()

            # Step 3: Backup each tenant DB
            for db_name in db_names:
                try:
                    await backup_single_db(db_name, timestamp)
                except Exception as tenant_error:
                    await flatbed("exception", f"In celery backup {db_name}: {tenant_error}")
                    continue  # move to next tenant

        except Exception as e:
            set_current_db("pardaaf_main")
            await flatbed("exception", f"In celery backup_all_tenants: {e}")
            return {"status": "error", "error": str(e)}

    # =====================
    # ✅ Celery + asyncio integration
    # =====================
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(run_for_all_tenants())


async def backup_single_db(db_name: str, timestamp: str):
    """
    Dump a single DB and push to rclone.
    """
    dump_file = f"/tmp/{db_name}_{timestamp}.dump"

    cmd = [
        "/usr/bin/pg_dump",
        "-h", os.getenv("DB_HOST", "localhost"),
        "-U", os.getenv("DB_USER", "postgres"),
        "-Fc",
        "-d", db_name,
        "-f", dump_file,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("DB_PASSWORD", "")

    subprocess.run(cmd, check=True, env=env)

    # Upload with rclone (your wrapper around subprocess)
    backup_to_gdrive(dump_file, db_name)

    await flatbed("info", f"Backup uploaded for {db_name} → {dump_file}")

    os.remove(dump_file)
