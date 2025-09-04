import subprocess


def backup_to_gdrive(local_file, db_name):
    remote_path = f"pardaaf_backups/{db_name}/daily/"

    remote = f"gdrive:{remote_path}{local_file.split('/')[-1]}"

    try:
        subprocess.run(
            ["rclone", "copy", local_file, remote, "--progress"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        raise e
