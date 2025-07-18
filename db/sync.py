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
