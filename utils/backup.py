import os
import subprocess


def backup_to_gdrive(local_file, period, db_name):
    rclone_bin = "/usr/bin/rclone"
    remote_dir = f"gdrive:pardaaf_backups/{db_name}/{period}/"
    remote = f"{remote_dir}{os.path.basename(local_file)}"

    # Retention policy
    keep = {"daily": "7d", "weekly": "8w", "monthly": "12M"}  # M = months
    retention = keep.get(period)

    try:
        # Upload
        subprocess.run([rclone_bin, "copy", local_file, remote, "--progress"], check=True)

        # Trim (skip yearly)
        if period in ("daily", "weekly", "monthly"):
            subprocess.run([rclone_bin, "delete", remote_dir, "--min-age", retention], check=True)

        return True
    except subprocess.CalledProcessError as e:
        raise e
