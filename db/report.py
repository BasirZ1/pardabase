from utils import flatbed
from utils.conn import connection_context


async def report_recent_activities_list(from_date, to_date):
    """
    Retrieve recent activities list according to start and end dates.

    Parameters:
    - from_date (str): From this date to the to_date.
    - to_date (str): From from_date to this date.

    Returns:
    - List of records from the admins_records table that match the criteria.
    """

    query = "SELECT id, date, username, action FROM admins_records WHERE date >= $1 AND date <= $2"

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, from_date, to_date)
    except Exception as e:
        await flatbed('exception', f"In report_recent_activities_list: {e}")
        raise RuntimeError(f"Failed to report_recent_activities_list: {e}")
