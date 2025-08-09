from helpers import get_formatted_tailors_list, get_formatted_salesmen_list, \
    get_formatted_suppliers_small_list
from utils import flatbed
from utils.conn import connection_context


async def insert_update_sync(key):
    try:
        async with connection_context() as conn:
            sql_insert = """
            INSERT INTO syncs (key, value) VALUES (
            $1, current_timestamp)
            ON CONFLICT (key) DO UPDATE SET value = current_timestamp
            RETURNING value;
            """
            value = await conn.fetchval(sql_insert, key)

            return value
    except Exception as e:
        await flatbed('exception', f"In insert_update_sync: {e}")
        return None


async def get_sync(key):
    try:
        async with connection_context() as conn:
            query = "SELECT value FROM syncs WHERE key = $1;"
            value = await conn.fetchval(query, key)

            return value
    except Exception as e:
        await flatbed('exception', f"In get_sync: {e}")
        return None


async def fetch_suppliers_list():
    """
    Retrieve all suppliers id and name from suppliers table.

    Returns:
    - All suppliers id and name from the suppliers table.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT id, name FROM suppliers;"
            suppliers_data = await conn.fetch(query)
            suppliers_list = get_formatted_suppliers_small_list(suppliers_data)
            return suppliers_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In fetch_suppliers_list: {e}")
        raise


async def fetch_salesmen_list():
    """
    Retrieve all salesmen user_id and full_name from users table where salesman_status is 'active'.

    Returns:
    - List of asyncpg Record objects with 'user_id' and 'full_name' of active salesmen.
    """
    try:
        async with connection_context() as conn:
            query = """
                SELECT u.user_id::TEXT, u.full_name
                FROM public.users u
                JOIN public.user_employment_info ei ON u.user_id = ei.user_id
                WHERE ei.salesman_status = 'active';
            """
            salesmen_data = await conn.fetch(query)
            salesmen_list = get_formatted_salesmen_list(salesmen_data)
            # Returns a list of asyncpg Record objects
            return salesmen_list

    except Exception as e:
        await flatbed('exception', f"In fetch_salesmen_list: {e}")
        raise


async def fetch_tailors_list():
    """
    Retrieve all tailors user_id and full_name from users table where tailor_type is not null.

    Returns:
    - List of asyncpg Records with 'user_id' and 'full_name' of tailors.
    """
    try:
        async with connection_context() as conn:
            query = """
                SELECT u.user_id::TEXT, u.full_name
                FROM public.users u
                JOIN public.user_employment_info ei ON u.user_id = ei.user_id
                WHERE ei.tailor_type IS NOT NULL;
            """
            tailors_data = await conn.fetch(query)
            tailors_list = get_formatted_tailors_list(tailors_data)
            return tailors_list

    except Exception as e:
        await flatbed('exception', f"In fetch_tailors_list: {e}")
        raise
