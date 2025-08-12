import uuid
from typing import Optional

from utils import flatbed
from utils.conn import connection_context


async def add_earning_to_user(userId, amount, currency, note, payed_by) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql_insert = """
                WITH inserted AS (
                    INSERT INTO user_payments (user_id, amount, currency, note, payed_by)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING user_id
                )
                SELECT u.username
                FROM inserted i
                JOIN users u ON u.user_id = i.user_id;
            """
            username = await conn.fetchval(sql_insert, userId, amount, currency, note, payed_by)

            return username
    except Exception as e:
        await flatbed('exception', f"In add_payment_to_user: {e}")
        return None


async def add_payment_to_supplier(supplierId, amount, currency, note, payed_by) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql_insert = """
                WITH inserted AS (
                    INSERT INTO supplier_payments (supplier_id, amount, currency, note, payed_by)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING supplier_id
                )
                SELECT s.name
                FROM inserted i
                JOIN suppliers s ON s.id = i.supplier_id;
            """
            supplier_name = await conn.fetchval(sql_insert, supplierId, amount, currency, note, payed_by)

            return supplier_name
    except Exception as e:
        await flatbed('exception', f"In add_payment_to_supplier: {e}")
        return None


async def get_supplier_payment_history_ps(supplier_id: int):
    """
    Retrieve payment history based on supplier ID

    Parameters:
    - supplier_id (int): The id of the supplier.

    Returns:
    - asyncpg.Record list: payment history with payer's name.
    """
    try:
        async with connection_context() as conn:
            query = """
                SELECT sp.id,
                       sp.amount,
                       sp.currency,
                       sp.note,
                       u.full_name AS payed_by_name,
                       sp.created_at
                FROM supplier_payments sp
                LEFT JOIN users u
                ON sp.payed_by = u.user_id
                WHERE sp.supplier_id = $1
                ORDER BY sp.created_at DESC;
            """
            payment_history = await conn.fetch(query, supplier_id)

            return payment_history or None

    except Exception as e:
        await flatbed('exception', f"In get_supplier_payment_history_ps: {e}")
        raise


async def get_user_payment_history_ps(user_id: str):
    """
    Retrieve payment history based on user_id

    Parameters:
    - user_id (str): The id for the user.

    Returns:
    - asyncpg.Record list: payment history with payer's name.
    """
    try:
        user_id = uuid.UUID(user_id)
        async with connection_context() as conn:
            query = """
                SELECT up.id,
                       up.amount,
                       up.currency,
                       up.note,
                       u.full_name AS payed_by_name,
                       up.created_at
                FROM user_payments up
                LEFT JOIN users u
                ON up.payed_by = u.user_id
                WHERE up.user_id = $1
                ORDER BY up.created_at DESC;
            """
            payment_history = await conn.fetch(query, user_id)

            return payment_history or None

    except Exception as e:
        await flatbed('exception', f"In get_user_payment_history_ps: {e}")
        raise
