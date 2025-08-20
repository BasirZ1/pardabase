from typing import Optional, List, Any

from helpers import get_date_range, parse_date
from utils import flatbed
from utils.conn import connection_context


async def insert_new_roll(product_code, purchase_item_id, quantity, color_letter):
    try:
        async with connection_context() as conn:
            sql_insert = """
                INSERT INTO rolls (
                    product_code,
                    purchase_item_id,
                    quantity,
                    color
                ) VALUES ($1, $2, $3, $4)
                RETURNING roll_code
            """
            roll_code = await conn.fetchval(sql_insert, product_code, purchase_item_id, quantity, color_letter)

            return roll_code
    except Exception as e:
        await flatbed('exception', f"In insert_new_roll: {e}")
        return None


async def update_roll(codeToEdit, quantity, color_letter):
    try:
        async with connection_context() as conn:
            sql_update = """
                UPDATE rolls
                SET quantity = $1,
                    color = $2, updated_at = now()
                WHERE roll_code = $3
            """
            await conn.execute(sql_update, quantity, color_letter, codeToEdit)

            return codeToEdit
    except Exception as e:
        await flatbed('exception', f"In update_roll: {e}")
        return None


async def add_roll_quantity_ps(roll_code, quantity) -> bool:
    try:
        async with connection_context() as conn:
            sql_update = """
                        UPDATE rolls
                        SET quantity = quantity + $1, updated_at = now()
                        WHERE roll_code = $2
                        RETURNING quantity
                    """
            updated_quantity = await conn.fetchval(sql_update, quantity, roll_code)

            return updated_quantity is not None

    except Exception as e:
        await flatbed('exception', f"In add_roll_quantity_ps: {e}")
        raise e


async def add_cut_fabric_tx(
    roll_code: str,
    quantity: int,
    created_by: str,
    status: str = 'manual',  # or 'draft'
    bill_code: Optional[str] = None,
    comment: Optional[str] = None,
) -> bool:
    try:
        async with connection_context() as conn:
            sql_insert = """
                INSERT INTO cut_fabric_tx (
                    roll_code,
                    bill_code,
                    quantity,
                    comment,
                    created_by,
                    status
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING roll_code
            """
            returned_roll_code = await conn.fetchval(
                sql_insert,
                roll_code,
                bill_code,
                quantity,
                comment,
                created_by,
                status
            )

            return returned_roll_code is not None
    except Exception as e:
        await flatbed('exception', f"In add_cut_fabric_tx: {e}")
        raise e


async def get_drafts_list_ps():
    """
    Retrieve all drafts from cut_fabric_tx table, including username.

    Returns:
    - All drafts from the cut_fabric_tx table, with username instead of created_by UUID.
    """
    try:
        async with connection_context() as conn:
            query = """
                SELECT 
                    tx.id,
                    tx.roll_code,
                    tx.bill_code,
                    u.username AS created_by,
                    tx.quantity,
                    tx.status,
                    tx.comment,
                    tx.created_at
                FROM cut_fabric_tx tx
                JOIN users u ON tx.created_by = u.user_id
                WHERE tx.status = $1
                ORDER BY tx.created_at
            """
            drafts_list = await conn.fetch(query, 'draft')
            return drafts_list

    except Exception as e:
        await flatbed('exception', f"In get_drafts_list_ps: {e}")
        raise


async def get_cutting_history_list_ps(
    status: Optional[str] = None,   # None / 'all' → every status except 'draft'
    date_idx: Optional[int] = None
):
    clauses: List[str] = []
    params:  List[Any] = []

    # status filter
    if status and status.lower() not in {"all", ""}:
        params.append(status)
        clauses.append(f"tx.status = ${len(params)}")
    else:
        clauses.append("tx.status <> 'draft'")

    # date filter
    dr = get_date_range(date_idx)
    if dr:
        start, end = dr
        params += [start, end]
        # placeholders are the two most‑recent params we just appended
        clauses.append(f"tx.created_at BETWEEN ${len(params)-1} AND ${len(params)}")

    where_sql = "WHERE " + " AND ".join(clauses)

    sql = f"""
        SELECT tx.id,
            tx.roll_code,
            tx.bill_code,
            u.username AS created_by,
            tx.quantity,
            tx.status,
            tx.comment,
            ru.username AS reviewed_by,
            tx.reviewed_at,
            tx.created_at
        FROM   cut_fabric_tx tx
        LEFT JOIN   users u ON tx.created_by = u.user_id
        LEFT JOIN users ru ON tx.reviewed_by = ru.user_id
        {where_sql}
        ORDER BY tx.created_at DESC;
    """

    try:
        async with connection_context() as conn:
            return await conn.fetch(sql, *params)
    except Exception as exc:
        await flatbed("exception", f"get_cutting_history_list_ps: {exc}")
        raise


async def get_cutting_history_list_for_roll_ps(
    code: str
):
    sql = f"""
        SELECT tx.id,
            tx.roll_code,
            tx.bill_code,
            u.username AS created_by,
            tx.quantity,
            tx.status,
            tx.comment,
            ru.username AS reviewed_by,
            tx.reviewed_at,
            tx.created_at
        FROM   cut_fabric_tx tx
        LEFT JOIN   users u ON tx.created_by = u.user_id
        LEFT JOIN users ru ON tx.reviewed_by = ru.user_id
        where tx.roll_code = $1
        ORDER BY tx.created_at DESC;
    """

    try:
        async with connection_context() as conn:
            return await conn.fetch(sql, code)
    except Exception as exc:
        await flatbed("exception", f"get_cutting_history_list_for_roll_ps: {exc}")
        raise


async def update_cut_fabric_tx_status_ps(
        _id: int,
        status: str,
        user_id: str
) -> bool:
    try:
        async with connection_context() as conn:
            sql_update = """
                        UPDATE cut_fabric_tx
                        SET status = $1,
                        reviewed_by = $2::uuid,
                        reviewed_at = now()
                        WHERE id = $3
                        RETURNING id
                    """
            return_id = await conn.fetchval(sql_update, status, user_id, _id)

            return return_id is not None

    except Exception as e:
        await flatbed('exception', f"In update_cut_fabric_tx_status: {e}")
        raise e

#
# async def get_rolls_list_for_sync(old_sync: str):
#     """
#     Retrieve rolls list based on last_sync compared to updated_at.
#     Parameters:
#         old_sync (str): The last sync date (ISO string). If None/empty → fetch all.
#     Returns:
#         List of records from the rolls table.
#     """
#     try:
#         async with connection_context() as conn:
#
#             if old_sync:
#                 last_sync_dt = parse_date(old_sync)
#                 query = "SELECT * FROM rolls WHERE updated_at > $1;"
#                 rolls_list = await conn.fetch(query, last_sync_dt)
#             else:
#                 query = "SELECT * FROM rolls;"
#                 rolls_list = await conn.fetch(query)
#
#             return rolls_list
#
#     except Exception as e:
#         await flatbed("exception", f"In get_rolls_list_for_sync: {e}")
#         raise


async def get_rolls_list_for_sync(old_sync: str):
    """
    Retrieve rolls list with extra field cost_per_metre (from purchase_items).
    Parameters:
        old_sync (str): The last sync date (ISO string). If None/empty → fetch all.
    Returns:
        List of records from the rolls table + cost_per_metre.
    """
    try:
        async with connection_context() as conn:
            last_sync_dt = parse_date(old_sync) if old_sync else None

            query = """
                SELECT 
                    r.*,
                    pi.cost_per_metre
                FROM rolls r
                LEFT JOIN purchase_items pi ON r.purchase_item_id = pi.id
                WHERE (
                    $1::timestamptz IS NULL
                    OR (r.updated_at > $1)
                )
            """

            rolls_list = await conn.fetch(query, last_sync_dt)
            return rolls_list

    except Exception as e:
        await flatbed("exception", f"In get_rolls_list_for_sync: {e}")
        raise


async def search_rolls_for_product(product_code):
    """
    Retrieve rolls list based on product_code.

    Parameters:
    - product_code (str): The code for the product to which the rolls belong.

    Returns:
    - List of records from the rolls table that match the product code.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT 
                r.product_code, 
                r.roll_code, 
                r.quantity, 
                r.color, 
                r.image_url,
                pi.cost_per_metre
            FROM rolls r
            LEFT JOIN purchase_items pi ON r.purchase_item_id = pi.id
            WHERE r.product_code = $1 AND r.archived = false
            """
            rolls_list = await conn.fetch(query, product_code)
            return rolls_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_rolls_for_product: {e}")
        raise


async def search_rolls_for_purchase_item(purchase_item_id):
    """
    Retrieve rolls list based on product_code.

    Parameters:
    - purchase_item_id (int): The id for the purchase item to which the rolls belong.

    Returns:
    - List of records from the rolls table that match the purchase item id.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT 
                r.product_code, 
                r.roll_code, 
                r.quantity, 
                r.color, 
                r.image_url,
                pi.cost_per_metre
            FROM rolls r
            LEFT JOIN purchase_items pi ON r.purchase_item_id = pi.id
            WHERE r.purchase_item_id = $1 AND r.archived = false
            """
            rolls_list = await conn.fetch(query, purchase_item_id)
            return rolls_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_rolls_for_purchase_item: {e}")
        raise


async def remove_roll_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM rolls WHERE roll_code = $1", code)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_roll_ps: {e}")
        return False


async def archive_roll_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("""
            UPDATE rolls
            SET archived = TRUE, updated_at = now()
            WHERE roll_code = $1
            """, code)
        return True
    except Exception as e:
        await flatbed('exception', f"in archive_roll_ps: {e}")
        return False
