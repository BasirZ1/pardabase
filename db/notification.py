from typing import Optional

from helpers import parse_date
from utils import flatbed
from utils.conn import connection_context


async def get_notifications_for_user_ps(user_id: str, level: int, old_sync: Optional[str] = None):
    if old_sync:
        old_sync = parse_date(old_sync)
    else:
        old_sync = parse_date('1970-01-01T00:00:00Z')  # fetch all if not provided

    try:
        async with connection_context() as conn:
            query = """
                select *
                from notifications n
                where (
                (n.target_user_id is not null and n.target_user_id = $1)
                or (n.target_roles is not null and $2 = any(n.target_roles))
                )
                and n.created_at > $3
                order by n.created_at desc
                limit 50;
            """
            notifications_list = await conn.fetch(query, user_id, level, old_sync)
            return notifications_list  # list of asyncpg.Record

    except Exception as e:
        await flatbed('exception', f"In get_notifications_for_user_ps: {e}")
        raise
