import random
import subprocess
import time

from helpers.celery import run_async
from utils import flatbed


def backup_to_gdrive(local_file, period, db_name):
    rclone_bin = "/usr/bin/rclone"
    remote_dir = f"gdrive:pardaaf_backups/{db_name}/{period}/"

    # Upload (WITH retries)
    run_rclone([
        rclone_bin, "copy",
        local_file, remote_dir,
        "--transfers", "1",
        "--checkers", "2",
        "--tpslimit", "5",
        "--tpslimit-burst", "5",
    ])

    return True


def cleanup_old_backups(period: str):
    # Retention policy
    keep = {"daily": "7d", "weekly": "8w", "monthly": "12M"}  # M = months
    retention = keep.get(period)

    run_rclone([
        "/usr/bin/rclone", "delete",
        "gdrive:pardaaf_backups",
        "--min-age", retention,
        "--include", f"/**/{period}/**",
        "--exclude", "*",
        "--transfers", "1",
        "--checkers", "2",
        "--tpslimit", "5",
    ])

    # TODO remove the flatbed
    run_async(flatbed("info", f"Backups cleaned up for {period}"))

    return True


def run_rclone(cmd, retries=5, base_delay=5):
    for attempt in range(retries):
        try:
            subprocess.run(cmd, check=True)
            return
        except subprocess.CalledProcessError:
            if attempt == retries - 1:
                raise
            sleep = base_delay * (2 ** attempt) + random.uniform(0, 3)
            time.sleep(sleep)
