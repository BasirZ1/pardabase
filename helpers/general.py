import os
from datetime import timedelta, datetime
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from fastapi import UploadFile

from utils import flatbed


async def classify_image_upload(upload: Optional[UploadFile]) -> Tuple[str, Optional[bytes]]:
    if upload is None:
        return "unchanged", None
    if upload.filename == "":
        return "remove", None
    return "update", await upload.read()
#
# def get_date_range(idx: Optional[int]) -> Optional[Tuple[datetime, datetime]]:
#     """Return (start, end) or None when idx is invalid/None."""
#     ranges = {0: 1, 1: 7, 2: 30, 3: 365}
#     days = ranges.get(idx)
#     if days is None:
#         return None
#     kabul_tz = ZoneInfo("Asia/Kabul")
#     end = datetime.now(kabul_tz)
#     return end - timedelta(days=days), end


def get_date_range(idx: Optional[int]) -> Optional[Tuple[datetime, datetime]]:
    """Return (start, end) datetime range in Kabul timezone."""
    ranges = {0: 1, 1: 7, 2: 30, 3: 365}
    days = ranges.get(idx)
    if days is None:
        return None

    kabul_tz = ZoneInfo("Asia/Kabul")
    now = datetime.now(kabul_tz)

    # Truncate to start of today
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)

    return start, end + timedelta(days=1)  # Make 'end' exclusive (next day's midnight)


def delete_temp_file(file_path: str):
    """
    Deletes the specified temporary file.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log the error if file deletion fails
        flatbed('exception', f"In delete temp file {file_path}: {e}")
