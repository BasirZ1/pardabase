from utils import flatbed
from utils.conn import connection_context


async def get_gallery_db_name(gallery_codename):
    """
        get gallery's db name from the main parda.af db.

        Args:
            gallery_codename (str): The gallery codename.

        Returns:
            str: The gallery db name.
        """
    try:
        async with connection_context() as conn:
            db_name = await conn.fetchval("""
                SELECT db_name FROM galleries WHERE gallery_codename = lower($1)
            """, gallery_codename)

            if not db_name:
                return None  # Username not found, abort

            return db_name
    except Exception as e:
        await flatbed('exception', f"In get_gallery_db_name: {e}")
        return None
