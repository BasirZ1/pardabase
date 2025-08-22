from typing import Optional

from utils import flatbed
from utils.conn import connection_context


async def add_earning_to_user(user_id, amount, earning_type, reference, note, added_by) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql_insert = """
                WITH inserted AS (
                    INSERT INTO user_earnings (user_id, amount, earning_type, reference, note, added_by)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING user_id
                )
                SELECT u.username
                FROM inserted i
                JOIN users u ON u.user_id = i.user_id;
            """
            username = await conn.fetchval(sql_insert, user_id, amount, earning_type, reference, note, added_by)

            return username
    except Exception as e:
        await flatbed('exception', f"In add_payment_to_user: {e}")
        return None


async def calculate_all_due_salaries_with_report_ps():
    try:
        async with connection_context() as conn:
            sql_query = """
                SELECT * FROM calculate_all_due_salaries_with_report();
            """
            result = await conn.fetchrow(sql_query)

            return result
    except Exception as e:
        await flatbed('exception', f"In calculate_all_due_salaries_with_report_ps: {e}")
        return None


async def get_users_earning_history_ps(user_id: str):
    """
        Retrieve earnings history for a user.

        Parameters:
            user_id (str): The user_id of the user.

        Returns:
            list[asyncpg.Record] | None: Earnings history for the given user.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT 
                ue.id,
                ue.amount,
                ue.earning_type,
                ue.reference,
                ue.note,
                ue.created_at,
                CASE 
                    WHEN ue.added_by = 'automated' THEN 'automated'
                    WHEN is_uuid(ue.added_by) THEN u.username
                    ELSE ue.added_by
                END AS added_by_display
            FROM user_earnings ue
            LEFT JOIN users u
                ON is_uuid(ue.added_by) 
                AND ue.added_by = u.user_id::text
            WHERE ue.user_id = $1
            ORDER BY ue.created_at DESC;
            """
            earnings_history = await conn.fetch(query, user_id)

            return earnings_history or None

    except Exception as e:
        await flatbed('exception', f"In get_users_earning_history_ps: {e}")
        raise
