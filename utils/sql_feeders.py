import json
from typing import Optional

from .logger import flatbed
from utils.conn import get_connection, release_connection


async def insert_new_product(image, name, category_index, cost_per_metre, price, description):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO products (
                image,
                name,
                category,
                cost_per_metre,
                price_per_metre,
                description
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING product_code
        """
        product_code = await conn.fetchval(sql_insert, image, name, category_index, cost_per_metre, price, description)
        return product_code
    except Exception as e:
        flatbed('exception', f"In insert_new_product: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_product(codeToEdit, image, name, category_index, cost_per_metre, price, description):
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE products
            SET image = $1, name = $2,
            category = $3, cost_per_metre = $4,
            price_per_metre = $5, description = $6
            WHERE product_code = $7
            RETURNING product_code
        """
        product_code = await conn.fetchval(sql_update, image, name,
                                           category_index, cost_per_metre, price, description, codeToEdit)

        return product_code is not None
    except Exception as e:
        flatbed('exception', f"in update_product: {e}")
        return False
    finally:
        await release_connection(conn)


async def update_roll_quantity_ps(roll_code, quantity, action):
    if action not in ["subtract", "add"]:
        flatbed('error', f"Invalid action: {action}. Expected 'subtract' or 'add'.")
        return False

    conn = await get_connection()
    try:
        # Using Python logic instead of relying on PostgreSQL CASE
        quantity = -quantity if action == "subtract" else quantity

        sql_update = """
                    UPDATE rolls
                    SET quantity = quantity + $1
                    WHERE roll_code = $2
                    RETURNING quantity
                """
        updated_quantity = await conn.fetchval(sql_update, quantity, roll_code)

        return updated_quantity is not None

    except Exception as e:
        flatbed('exception', f"In update_roll_quantity_ps: {e}")
        return False
    finally:
        await release_connection(conn)


async def add_expense_ps(category_index, description, amount):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO expenses (category_index, description, amount)
            VALUES ($1, $2, $3)
            RETURNING id;
        """
        expense_id = await conn.fetchval(sql_insert, category_index, description, amount)

        return expense_id
    except Exception as e:
        flatbed('exception', f"In add_expense: {e}")
        return None
    finally:
        await release_connection(conn)


async def insert_new_roll(product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO rolls (
                product_code,
                quantity,
                color,
                sample_image
            ) VALUES ($1, $2, $3, $4)
            RETURNING roll_code
        """
        roll_code = await conn.fetchval(sql_insert, product_code, quantity, color_letter, image_data)

        return f"{product_code}{roll_code}" if roll_code else None
    except Exception as e:
        flatbed('exception', f"In insert_new_roll: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_roll(codeToEdit, product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE rolls
            SET quantity = $1,
                color = $2,
                sample_image = $3
            WHERE roll_code = $4
        """
        await conn.execute(sql_update, quantity, color_letter, image_data, codeToEdit)

        return f"{product_code}{codeToEdit}"
    except Exception as e:
        flatbed('exception', f"In update_roll: {e}")
        return None
    finally:
        await release_connection(conn)


async def insert_new_bill(
        bill_date: Optional[str] = None,
        due_date: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_number: Optional[str] = None,
        price: Optional[int] = None,
        paid: Optional[int] = None,
        remaining: Optional[int] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        status: Optional[str] = 'pending',
        salesman: Optional[str] = None,
        tailor: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO bills (
                bill_date,
                due_date,
                customer_name,
                customer_number,
                price,
                paid,
                remaining,
                fabrics,
                parts,
                status,
                salesman,
                tailor,
                additional_data,
                installation
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12, $13::jsonb, $14)
            RETURNING bill_code
        """

        bill_code = await conn.fetchval(
            sql_insert,
            bill_date,
            due_date,
            customer_name,
            customer_number,
            price,
            paid,
            remaining,
            fabrics,
            parts,
            status,
            salesman,
            tailor,
            additional_data,
            installation
        )
        return bill_code
    except Exception as e:
        flatbed('exception', f"In insert_new_bill: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_bill(
        bill_code: str,
        due_date: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_number: Optional[str] = None,
        price: Optional[int] = None,
        paid: Optional[int] = None,
        remaining: Optional[int] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET due_date = $1,
                customer_name = $2,
                customer_number = $3,
                price = $4,
                paid = $5,
                remaining = $6,
                fabrics = $7::jsonb,
                parts = $8::jsonb,
                additional_data = $9::jsonb,
                installation = $10,
                updated_at = NOW()
            WHERE bill_code = $11
        """
        await conn.execute(
            sql_update,
            due_date,
            customer_name,
            customer_number,
            price,
            paid,
            remaining,
            json.loads(fabrics) if fabrics else None,
            json.loads(parts) if parts else None,
            json.loads(additional_data) if additional_data else None,
            installation,
            bill_code
        )
        return bill_code
    except Exception as e:
        flatbed('exception', f"In update_bill: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_bill_status_ps(bill_code: str, status: str) -> bool:
    """
    Update a bill's status in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        status (str): The new status for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET status = $1
            WHERE bill_code = $2
            RETURNING status
        """
        updated_status = await conn.fetchval(sql_update, status, bill_code)

        return updated_status is not None
    except Exception as e:
        flatbed('exception', f"In update_bill_status_ps: {e}")
        return False
    finally:
        await release_connection(conn)


async def update_bill_tailor_ps(bill_code: str, tailor: str) -> bool:
    """
    Update a bill's tailor in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        tailor (str): The tailor for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET tailor = $1
            WHERE bill_code = $2
            RETURNING tailor
        """
        updated_tailor = await conn.fetchval(sql_update, tailor, bill_code)

        return updated_tailor is not None
    except Exception as e:
        flatbed('exception', f"In update_bill_tailor_ps: {e}")
        return False
    finally:
        await release_connection(conn)
