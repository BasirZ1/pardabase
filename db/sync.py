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
    # Replace with actual DB call
    return [{"id": 1, "name": "Supplier A"}, {"id": 2, "name": "Supplier B"}]


async def fetch_salesmen_list():
    # Replace with actual DB call
    return [{"userId": "uuid1", "fullName": "Salesman One"}, {"userId": "uuid2", "fullName": "Salesman Two"}]


async def fetch_tailors_list():
    # Replace with actual DB call
    return [{"userId": "uuid3", "fullName": "Tailor One"}]
