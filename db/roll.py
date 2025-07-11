from typing import Optional

from utils import flatbed
from utils.conn import connection_context


async def insert_new_roll(product_code, quantity, color_letter):
    try:
        async with connection_context() as conn:
            sql_insert = """
                INSERT INTO rolls (
                    product_code,
                    quantity,
                    color
                ) VALUES ($1, $2, $3)
                RETURNING roll_code
            """
            roll_code = await conn.fetchval(sql_insert, product_code, quantity, color_letter)

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
                    color = $2
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
                        SET quantity = quantity + $1
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


async def update_cut_fabric_tx_status_ps(
        _id: int,
        status: str,
        username: str
) -> bool:
    try:
        async with connection_context() as conn:
            sql_update = """
                        UPDATE cut_fabric_tx
                        SET status = $1,
                        reviewed_by = $2,
                        reviewed_at = now()
                        WHERE id = $3
                        RETURNING id
                    """
            return_id = await conn.fetchval(sql_update, status, username, _id)

            return return_id is not None

    except Exception as e:
        await flatbed('exception', f"In update_cut_fabric_tx_status: {e}")
        raise e


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
            SELECT product_code, roll_code, quantity, color, image_url 
            FROM rolls
            WHERE product_code = $1
            """
            rolls_list = await conn.fetch(query, product_code)
            return rolls_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_rolls_for_product: {e}")
        raise RuntimeError(f"Failed to search rolls: {e}")


async def remove_roll_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM rolls WHERE roll_code = $1", code)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_roll_ps: {e}")
        return False
