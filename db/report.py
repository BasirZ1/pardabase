import datetime

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

    if from_date:
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()\
            if isinstance(from_date, str) else from_date

    if to_date:
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()\
            if isinstance(to_date, str) else to_date

    query = "SELECT id, date, username, action FROM admins_records WHERE date >= $1 AND date <= $2"

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, from_date, to_date)
    except Exception as e:
        await flatbed('exception', f"In report_recent_activities_list: {e}")
        raise RuntimeError(f"Failed to report_recent_activities_list: {e}")


async def report_tags_list(from_date, to_date):
    """
    Retrieve tags list with fullCode and productName according to dates.
    """

    if from_date:
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() \
            if isinstance(from_date, str) else from_date

    if to_date:
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date() \
            if isinstance(to_date, str) else to_date

    query = """
    SELECT
        (products.product_code || rolls.roll_code) AS full_code,
        products.name AS product_name,
        rolls.color AS color,
        rolls.created_on AS created_on
    FROM
        rolls
    INNER JOIN
        products
    ON
        rolls.product_code = products.product_code
    WHERE
        rolls.created_on >= $1 AND rolls.created_on <= $2
    ORDER BY
        rolls.created_on
    """

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, from_date, to_date)
    except Exception as e:
        await flatbed('exception', f"In report_tags_list: {e}")
        raise RuntimeError(f"Failed to report_tags_list: {e}")
