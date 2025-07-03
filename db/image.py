from typing import Optional

from utils import upload_image_to_r2, flatbed, delete_image_from_r2
from utils.conn import connection_context


async def handle_image_update(_type: str, tenant: str, code: str, status: str,
                              image_data: Optional[bytes]) -> Optional[str]:
    if status == "update":
        return await update_image_bucket_db(_type, tenant, code, image_data)
    elif status == "remove":
        return await remove_image_bucket_db(_type, tenant, code)


async def update_image_bucket_db(_type: str, tenant: str, code: str, image_data: bytes) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql = get_image_update_sql(_type)
            image_url = await upload_image_to_r2(_type, tenant, code, image_data)
            await conn.execute(sql, image_url, code)
            return image_url
    except Exception as e:
        await flatbed('exception', f"In update_image_bucket_db: {e}")
        return None


async def remove_image_bucket_db(_type: str, tenant: str, code: str) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql = get_image_update_sql(_type)
            await delete_image_from_r2(_type, tenant, code)
            await conn.execute(sql, None, code)
            return "Success"
    except Exception as e:
        await flatbed('exception', f"In remove_image_bucket_db: {e}")
        return "Failed"


def get_image_update_sql(_type: str) -> str:
    if _type == "product":
        return "UPDATE products SET image_url = $1 WHERE product_code = $2"
    elif _type == "roll":
        return "UPDATE rolls SET image_url = $1 WHERE roll_code = $2"
    elif _type == "user":
        return "UPDATE users SET image_url = $1 WHERE username = $2"
    else:
        raise ValueError(f"Unsupported type for image update: {_type}")
