from typing import Optional

from helpers.format_list import make_entity_dic, make_entity_details_dic
from utils import flatbed
from utils.conn import connection_context


async def insert_new_entity(
        name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
):
    """
    Adds a new entity to the database.

    Args:
        name (str): The name of the entity.
        phone (Optional[str]): The phone number of the entity.
        address (Optional[str]): The address of the entity.
        notes (Optional[str]): Notes and data about the entity.

    Returns:
        entity_id: If the entity was added successfully, return entity_id else none.
    """

    try:
        async with connection_context() as conn:

            sql_insert = """
                INSERT INTO entities (name, phone, address, notes) 
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """

            entity_id = await conn.fetchval(sql_insert, name, phone, address, notes)
            return entity_id

    except Exception as e:
        await flatbed('exception', f"in insert_new_entity: {e}")
        return None


async def update_entity(
        idToEdit: int,
        name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
):
    """
    Updates entity details in the database.

    Args:
        idToEdit (str): The id of the entity to be updated.
        name (str): The new name of the entity.
        phone (Optional[str]): The phone number of the entity.
        address (Optional[str]): The address of the entity.
        notes (Optional[str]): Notes and data about the entity.

    Returns:
        entity_id: If the update was successful, return entity_id else None.
    """
    try:
        async with connection_context() as conn:

            sql_update = f"""
                UPDATE entities
                SET name = $1, phone = $2, address = $3, notes = $4
                WHERE id = $5
                RETURNING id
            """

            entity_id = await conn.fetchval(sql_update, name, phone, address, notes, idToEdit)
            return entity_id

    except Exception as e:
        await flatbed('exception', f"In update_entity: {e}")
        return None


async def get_entity_ps(entity_id: int):
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow("""
                               SELECT * FROM entities
                               WHERE id = $1
                           """, entity_id)
            if data:
                entity = make_entity_dic(data)
                return entity

            return None
    except Exception as e:
        await flatbed('exception', f"In get_entity_ps: {e}")
        raise


async def get_entities_list_ps():
    """
    Retrieve all entities from entities table.

    Returns:
    - All entities from the entities table.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM entities;"
            entities_list = await conn.fetch(query)
            return entities_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In get_entities_list_ps: {e}")
        raise


async def get_entity_details_ps(entity_id: int):
    """
     Retrieve an entity's details like payable and receivable totals per currency.
     """
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow(
                """
                SELECT
                    -- payable: what you owe them (in minus any offsets)
                    COALESCE(SUM(CASE WHEN direction = 'in' AND currency = 'AFN' THEN amount ELSE 0 END), 0)
                    AS payable_total_afn,
                    COALESCE(SUM(CASE WHEN direction = 'in' AND currency = 'USD' THEN amount ELSE 0 END), 0) 
                    AS payable_total_usd,
                    COALESCE(SUM(CASE WHEN direction = 'in' AND currency = 'CNY' THEN amount ELSE 0 END), 0)
                    AS payable_total_cny,
                    
                    -- receivable: what they owe you (out minus any offsets)
                    COALESCE(SUM(CASE WHEN direction = 'out' AND currency = 'AFN' THEN amount ELSE 0 END), 0)
                    AS receivable_total_afn,
                    COALESCE(SUM(CASE WHEN direction = 'out' AND currency = 'USD' THEN amount ELSE 0 END), 0)
                    AS receivable_total_usd,
                    COALESCE(SUM(CASE WHEN direction = 'out' AND currency = 'CNY' THEN amount ELSE 0 END), 0)
                    AS receivable_total_cny
                FROM misc_transactions
                WHERE entity_id = $1
            """, entity_id)

            return make_entity_details_dic(data)

    except Exception as e:
        await flatbed('exception', f"In get_entity_details_ps: {e}")
        raise


async def remove_entity_ps(entity_id: int):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM entities WHERE id = $1", entity_id)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_entity_ps: {e}")
        return False
