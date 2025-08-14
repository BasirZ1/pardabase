from typing import Optional

from helpers.format_list import make_entity_dic
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


# async def get_entity_details_ps(entity_id: int):
#     """
#      Retrieve a entity's details like aggregated totals for purchases, payments,
#      and miscellaneous transactions per currency.
#      """
#     try:
#         async with connection_context() as conn:
#             data = await conn.fetchrow("""
#                 WITH purchase_totals AS (
#                     SELECT
#                         SUM(CASE WHEN currency = 'AFN' THEN total_amount ELSE 0 END) AS purchases_total_afn,
#                         SUM(CASE WHEN currency = 'USD' THEN total_amount ELSE 0 END) AS purchases_total_usd,
#                         SUM(CASE WHEN currency = 'CNY' THEN total_amount ELSE 0 END) AS purchases_total_cny
#                     FROM purchases
#                     WHERE archived = FALSE AND entity_id = $1
#                 ),
#                 payment_totals AS (
#                     SELECT
#                         SUM(CASE WHEN currency = 'AFN' THEN amount ELSE 0 END) AS total_paid_afn,
#                         SUM(CASE WHEN currency = 'USD' THEN amount ELSE 0 END) AS total_paid_usd,
#                         SUM(CASE WHEN currency = 'CNY' THEN amount ELSE 0 END) AS total_paid_cny
#                     FROM entity_payments
#                     WHERE entity_id = $1
#                 ),
#                 misc_totals AS (
#                     SELECT
#                         SUM(CASE WHEN currency = 'AFN' THEN amount ELSE 0 END) AS miscellaneous_total_afn,
#                         SUM(CASE WHEN currency = 'USD' THEN amount ELSE 0 END) AS miscellaneous_total_usd,
#                         SUM(CASE WHEN currency = 'CNY' THEN amount ELSE 0 END) AS miscellaneous_total_cny
#                     FROM misc_transactions
#                     WHERE entity_id = $1
#                 )
#                 SELECT
#                     COALESCE(pt.purchases_total_afn, 0) AS purchases_total_afn,
#                     COALESCE(pt.purchases_total_usd, 0) AS purchases_total_usd,
#                     COALESCE(pt.purchases_total_cny, 0) AS purchases_total_cny,
#                     COALESCE(pay.total_paid_afn, 0) AS total_paid_afn,
#                     COALESCE(pay.total_paid_usd, 0) AS total_paid_usd,
#                     COALESCE(pay.total_paid_cny, 0) AS total_paid_cny,
#                     COALESCE(mt.miscellaneous_total_afn, 0) AS miscellaneous_total_afn,
#                     COALESCE(mt.miscellaneous_total_usd, 0) AS miscellaneous_total_usd,
#                     COALESCE(mt.miscellaneous_total_cny, 0) AS miscellaneous_total_cny
#                 FROM purchase_totals pt, payment_totals pay, misc_totals mt
#             """, entity_id)
#
#             if data:
#                 entity_details = make_entity_details_dic(data)
#                 return entity_details
#
#             return None
#     except Exception as e:
#         await flatbed('exception', f"In get_entity_details_ps: {e}")
#         raise


async def remove_entity_ps(entity_id: int):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM entities WHERE id = $1", entity_id)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_entity_ps: {e}")
        return False
