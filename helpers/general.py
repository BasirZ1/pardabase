import os
from datetime import timedelta, datetime
from typing import Optional, Tuple

from fastapi import UploadFile

from utils import flatbed


async def classify_image_upload(upload: Optional[UploadFile]) -> Tuple[str, Optional[bytes]]:
    if upload is None:
        return "unchanged", None
    if upload.filename == "":
        return "remove", None
    return "update", await upload.read()


def get_date_range(_date: int):
    """
    Calculate the date range based on the `date` parameter.

    Parameters:
    - date (int): The date filter options index (e.g., 'Today', 'Last 7 days', 'Last 30 days', 'All').

    Returns:
    - Tuple of (start_date, end_date) if the date is valid; otherwise, returns None.
    """
    end_date = datetime.now()  # Current date and time

    if _date == 0:
        start_date = end_date - timedelta(days=1)
    elif _date == 1:
        start_date = end_date - timedelta(days=7)
    elif _date == 2:
        start_date = end_date - timedelta(days=30)  # Approximate 1 month as 30 days
    elif _date == 3:
        start_date = end_date - timedelta(days=365)  # Example: Last year
    else:
        return None  # Invalid date parameter, return None

    return start_date, end_date


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
