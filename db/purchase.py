from typing import Optional, Any

from utils import flatbed
from utils.conn import connection_context


async def insert_new_purchase(
        supplier_id: int,
        total_amount: Optional[int] = None,
        currency: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
) -> tuple[Any, Any, Any, Any] | None:
    try:
        async with connection_context() as conn:

            sql_insert = """
                WITH inserted AS (
                    INSERT INTO purchases (
                        supplier_id,
                        total_amount,
                        currency,
                        description,
                        created_by
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, created_at, updated_at, created_by
                )
                SELECT 
                    inserted.id,
                    inserted.created_at,
                    inserted.updated_at,
                    users.full_name AS created_by_name
                FROM inserted
                JOIN users ON users.user_id = inserted.created_by
            """

            row = await conn.fetchrow(
                sql_insert,
                supplier_id,
                total_amount,
                currency,
                description,
                user_id
            )
            if row:
                return row['id'], row['created_at'], row['updated_at'], row['created_by_name']
            else:
                return None
    except Exception as e:
        await flatbed('exception', f"In insert_new_purchase: {e}")
        return None


async def update_purchase(
        purchase_id: int,
        supplier_id: int,
        total_amount: Optional[int] = None,
        currency: Optional[str] = None,
        description: Optional[str] = None,
) -> tuple[Any, Any] | None:
    try:
        async with connection_context() as conn:

            sql_update = """
                UPDATE purchases
                SET supplier_id = $1,
                    total_amount = $2,
                    currency = $3,
                    description = $4,
                    updated_at = NOW()
                WHERE id = $5
                RETURNING id, updated_at
            """
            row = await conn.fetchrow(
                sql_update,
                supplier_id,
                total_amount,
                currency,
                description,
                purchase_id,
            )
            if row:
                return row['id'], row['updated_at']
            else:
                return None
    except Exception as e:
        await flatbed('exception', f"In update_purchase: {e}")
        return None


async def insert_new_purchase_item(
        purchase_id: int,
        product_code: str,
        cost_per_metre: int
) -> int | None:
    try:
        async with connection_context() as conn:

            sql_insert = """
                INSERT INTO purchase_items (
                    purchase_id,
                    product_code,
                    cost_per_metre
                ) VALUES ($1, $2, $3)
                RETURNING id
            """

            purchase_item_id = await conn.fetchval(
                sql_insert,
                purchase_id,
                product_code,
                cost_per_metre
            )
            if purchase_item_id:
                return purchase_item_id
            else:
                return None
    except Exception as e:
        await flatbed('exception', f"In insert_new_purchase_item: {e}")
        return None


async def update_purchase_item(
        id_to_edit: int,
        purchase_id: int,
        productCode: str,
        cost_per_metre: int
) -> int | None:
    try:
        async with connection_context() as conn:

            sql_update = """
                UPDATE purchase_items
                SET purchase_id = $1,
                    product_code = $2,
                    cost_per_metre = $3
                WHERE id = $4
                RETURNING id
            """
            purchase_item_id = await conn.fetchval(
                sql_update,
                purchase_id,
                productCode,
                cost_per_metre,
                id_to_edit
            )
            if purchase_item_id:
                return purchase_item_id
            else:
                return None
    except Exception as e:
        await flatbed('exception', f"In update_purchase_item: {e}")
        return None


# async def search_purchases_list(search_query, search_by):
#     """
#     Retrieve purchases list based on a search query and filter with search_by.
#
#     Parameters:
#     - search_query (str): The term to search within the specified field.
#     - search_by (int): The field to search in:
#         0 for 'purchase_id',
#         1 for 'supplier_id'
#
#     Returns:
#     - List of records from the purchases table that match the criteria.
#     """
#     try:
#         async with connection_context() as conn:
#             query = "SELECT * FROM search_purchases_list($1, $2);"
#             purchases_list = await conn.fetch(query, search_query, search_by)
#             return purchases_list  # Returns a list of asyncpg Record objects
#
#     except Exception as e:
#         await flatbed('exception', f"In search_purchases_list: {e}")
#         raise RuntimeError(f"Failed to search purchases: {e}")


async def search_purchases_list_filtered(_date):
    """
    Retrieve purchases list based on a date filter.

    Parameters:
    - date (int): The date filter for purchases list.

    Returns:
    - List of records from the purchases table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_purchases_list_filtered($1);"
            purchases_list = await conn.fetch(query, _date)
            return purchases_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_purchases_list_filtered: {e}")
        raise RuntimeError(f"Failed to search purchases: {e}")


async def get_purchase_items_ps(purchase_id):
    """
    Retrieve purchase items with product names for a particular purchase.

    Parameters:
    - purchase_id (int): ID of the purchase.

    Returns:
    - List of records including purchase item fields and the product name.
    """
    try:
        async with connection_context() as conn:
            query = """
                SELECT pi.*, p.name AS product_name
                FROM purchase_items pi
                JOIN products p ON pi.product_code = p.product_code
                WHERE pi.purchase_id = $1;
            """
            purchase_items = await conn.fetch(query, purchase_id)
            return purchase_items  # Each record includes product_name

    except Exception as e:
        await flatbed('exception', f"In get_purchase_items_ps: {e}")
        raise RuntimeError(f"Failed to get purchase items: {e}")


# async def get_purchase_ps(purchase_id):
#     """
#     Retrieve purchase based on purchase_id (Async Version for asyncpg).
#
#     Parameters:
#     - purchase_id (int): The id for the specified purchase.
#
#     Returns:
#     - dict: A single purchase record for the specified purchase.
#     """
#     try:
#         async with connection_context() as conn:
#             query = "SELECT * FROM search_purchases_list($1, $2, 1, true);"
#             data = await conn.fetchrow(query, purchase_id, 0)
#
#             if data:
#                 purchase = make_purchase_dic(data)
#                 return purchase
#
#             return None
#
#     except Exception as e:
#         await flatbed('exception', f"In get_purchase_ps: {e}")
#         return None
#


async def remove_purchase_ps(purchase_id):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM purchases WHERE id = $1", purchase_id)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_purchase_ps: {e}")
        return False


async def archive_purchase_ps(purchase_id):
    try:
        async with connection_context() as conn:
            await conn.execute("""
            UPDATE purchases
            SET archived = TRUE, updated_at = now()
            WHERE id = $1
            """, purchase_id)
        return True
    except Exception as e:
        await flatbed('exception', f"in archive_purchase_ps: {e}")
        return False
