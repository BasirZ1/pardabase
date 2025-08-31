from utils import flatbed
from utils.conn import connection_context


async def get_notifications_for_user_ps(user_id: str, level: int):
    """
    Retrieve all notifications for a specific user from notifications table.

    Returns:
    - All users from the notifications table.
    """
    try:
        async with connection_context() as conn:
            query = """
                select *
                from notifications n
                join users u on u.user_id = $1  -- current user
                where
                    n.target_user_id = u.user_id  -- personal notifications
                    or ($2 = ANY(n.target_roles)) -- role-based
                order by n.created_at desc
                limit 50;
            """
            notifications_list = await conn.fetch(query, user_id, level)
            return notifications_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In get_notifications_for_user_ps: {e}")
        raise
