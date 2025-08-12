from typing import Optional

from utils import flatbed
from utils.conn import connection_context


async def add_miscellaneous_record_ps(
    amount: int,
    currency: str,
    direction: str,
    supplier_id: Optional[int] = None,
    entity_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    note: Optional[str] = None,
    created_by: Optional[str] = None
) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql_insert = """
                WITH inserted AS (
                    INSERT INTO misc_transactions (
                        supplier_id, entity_id, transaction_type,
                        amount, currency, direction, note, created_by
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING supplier_id, entity_id
                )
                SELECT COALESCE(s.name, e.name) AS name
                FROM inserted i
                LEFT JOIN suppliers s ON s.id = i.supplier_id
                LEFT JOIN entities e ON e.id = i.entity_id;
            """
            return await conn.fetchval(
                sql_insert,
                supplier_id, entity_id, transaction_type,
                amount, currency, direction, note, created_by
            )
    except Exception as e:
        await flatbed('exception', f"add_miscellaneous_record: {e}")
        return None


async def search_miscellaneous_records_for_supplier(supplier_id):
    """
    Retrieve miscellaneous records based on supplier_id.

    Parameters:
    - supplier_id (int): The supplier id for which to retrieve miscellaneous records.

    Returns:
    - List of records from the misc_transactions table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT
                mt.id,
                mt.transaction_type,
                mt.amount,
                mt.currency,
                mt.direction,
                mt.note,
                u.username AS created_by,
                mt.created_at
            FROM misc_transactions mt
            LEFT JOIN users u ON mt.created_by = u.user_id
            WHERE
                mt.supplier_id = $1
            ORDER BY mt.created_at DESC;
            """
            misc_records = await conn.fetch(query, supplier_id)
            return misc_records  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_miscellaneous_records_for_supplier: {e}")
        raise
