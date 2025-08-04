from typing import Optional

from utils import flatbed
from utils.conn import connection_context


async def add_payment_to_user(userId, amount, currency, note, payed_by) -> Optional[str]:
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
