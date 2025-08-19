from helpers import parse_date
from utils import flatbed
from utils.conn import connection_context


# async def report_recent_activities_list(from_date, to_date):
#     """
#     Retrieve recent activities list according to start and end dates.
#
#     Parameters:
#     - from_date (str): From this date to the to_date.
#     - to_date (str): From from_date to this date.
#
#     Returns:
#     - List of records from the admins_records table that match the criteria.
#     """
#
#     if from_date:
#         from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()\
#             if isinstance(from_date, str) else from_date
#
#     if to_date:
#         to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()\
#             if isinstance(to_date, str) else to_date
#
#     query = "SELECT id, date, username, action FROM admins_records WHERE date >= $1 AND date <= $2"
#     query = """
#         SELECT
#             ar.id,
#             ar.date,
#             u.username,
#             ar.action
#         FROM admins_records ar
#         LEFT JOIN users u ON ar.user_id = u.user_id
#         WHERE ar.date >= $1 AND ar.date <= $2
#         ORDER BY ar.date DESC
#     """
#     try:
#         async with connection_context() as conn:
#             return await conn.fetch(query, from_date, to_date)
#     except Exception as e:
#         await flatbed('exception', f"In report_recent_activities_list: {e}")
#         raise
#
#
# import datetime

async def report_recent_activities_list(from_date, to_date):
    """
    Retrieve recent activities list according to start and end dates.

    Parameters:
    - from_date (str|date): Start date.
    - to_date (str|date): End date.

    Returns:
    - List of records from the admins_records table that match the criteria.
    """
    if from_date:
        from_date = parse_date(from_date)

    if to_date:
        to_date = parse_date(to_date)

    query = """
        SELECT 
            ar.id,
            ar.date,
            u.username,
            ar.action
        FROM admins_records ar
        LEFT JOIN users u ON ar.user_id = u.user_id
        WHERE ar.date >= $1 AND ar.date <= $2
        ORDER BY ar.date DESC
    """

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, from_date, to_date)
    except Exception as e:
        await flatbed('exception', f"In report_recent_activities_list: {e}")
        raise


async def report_tags_list(from_date, to_date):
    """
    Retrieve tags list with fullCode and productName according to dates.
    """

    from_date = parse_date(from_date)

    to_date = parse_date(to_date)

    query = """
    SELECT
        (rolls.product_code || rolls.roll_code) AS full_code,
        products.name AS product_name,
        products.category AS category,
        rolls.color AS color,
        rolls.created_at AS created_at,
        rolls.image_url AS image_url
    FROM
        rolls
    INNER JOIN
        products
    ON
        rolls.product_code = products.product_code
    WHERE
        rolls.created_at >= $1 AND rolls.created_at <= $2
    ORDER BY
        rolls.created_at
    """

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, from_date, to_date)
    except Exception as e:
        await flatbed('exception', f"In report_tags_list: {e}")
        raise
