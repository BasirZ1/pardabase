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


async def search_miscellaneous_records(_id: int, _type: str, direction: str):
    """
    Retrieve miscellaneous records based on id and type.

    Parameters:
        _id (int): The id for which to retrieve miscellaneous records (supplier_id or entity_id).
        _type (str): "supplier" or "entity".
        direction (str): "in" or "out".

    Returns:
        list[asyncpg.Record]: Miscellaneous records that match the criteria.
    """
    try:
        async with connection_context() as conn:
            if _type == "supplier":
                where_clause = "mt.supplier_id = $1 AND mt.direction = $2"
            elif _type == "entity":
                where_clause = "mt.entity_id = $1 AND mt.direction = $2"
            else:
                raise ValueError("type must be 'supplier' or 'entity'")

            query = f"""
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
                WHERE {where_clause}
                ORDER BY mt.created_at DESC;
            """

            misc_records = await conn.fetch(query, _id, direction)
            return misc_records  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_miscellaneous_records: {e}")
        raise
