from helpers import get_date_range
from utils import flatbed
from utils.conn import connection_context


async def get_dashboard_data_ps():
    """
    Retrieve dashboard data from the stored procedure `get_dashboard_data`.

    Returns:
    - dict: A dictionary containing totalBills, billsCompleted, billsPending, and totalProducts.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM get_dashboard_data();"
            data = await conn.fetchrow(query)

            if not data:
                raise ValueError("No data returned from get_dashboard_data()")

            dashboard_data = {
                "totalBills": data["total_bills"],
                "billsCompleted": data["bills_completed"],
                "billsPending": data["bills_pending"],
                "totalProducts": data["total_products"]
            }
            return dashboard_data

    except Exception as e:
        await flatbed('exception', f"In get_dashboard_data_ps: {e}")
        raise RuntimeError(f"Failed to get dashboard data: {e}")


async def search_recent_activities_list(_date):
    """
    Retrieve recent activities list and filter with date range.

    Parameters:
    - _date (int): Date range filter index ('last week', 'last month', 'last year', 'last day').

    Returns:
    - List of records from the admins_records table that match the criteria.
    """

    query = "SELECT id, date, username, action FROM admins_records WHERE 1=1"
    params = []

    date_range = get_date_range(_date)

    if date_range:
        start_date, end_date = date_range
        query += " AND date >= $1 AND date <= $2"
        params.extend([start_date, end_date])

    limit = {0: 10, 1: 20, 2: 30}.get(_date)
    if limit:
        query += f" ORDER BY date DESC LIMIT {limit}"
    else:
        query += " ORDER BY date DESC"

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, *params)
    except Exception as e:
        await flatbed('exception', f"In search_recent_activities_list: {e}")
        raise RuntimeError(f"Failed to search_recent_activities_list: {e}")
