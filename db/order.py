from typing import Optional

from utils import flatbed
from utils.conn import connection_context


async def insert_new_online_order(
        first_name: str,
        phone: str,
        country: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        payment_method: str,
        cart_items: str,
        total_amount: int,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        notes: Optional[str] = None
) -> Optional[str]:
    try:
        async with connection_context() as conn:
            sql_insert = """
                INSERT INTO online_orders (
                    first_name,
                    last_name,
                    phone,
                    email,
                    country,
                    address,
                    city,
                    state,
                    zip_code,
                    payment_method,
                    cart_items,
                    total_amount,
                    notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::jsonb, $12, $13)
                RETURNING id
            """

            order_id = await conn.fetchval(
                sql_insert,
                first_name,
                last_name,
                phone,
                email,
                country,
                address,
                city,
                state,
                zip_code,
                payment_method,
                cart_items,
                total_amount,
                notes
            )
            return order_id
    except Exception as e:
        await flatbed('exception', f"In insert_new_online_order: {e}")
        return None


async def subscribe_newsletter_ps(
        email: str
) -> str:
    try:
        async with connection_context() as conn:
            # Standardize email to lowercase
            email_lower = email.lower()

            # Check if the email already exists and whether it is verified
            sql_check = """
                SELECT token, is_verified 
                FROM newsletter_emails 
                WHERE email = $1
            """
            existing_email = await conn.fetchrow(sql_check, email_lower)

            if existing_email:
                # If email exists and is verified
                if existing_email["is_verified"]:
                    return "subscribed"
                # If email exists but not verified, return the existing token for verification
                return existing_email["token"]

            # Insert the new email and return the generated token
            sql_insert = """
                INSERT INTO newsletter_emails (email)
                VALUES ($1)
                RETURNING token
            """
            token = await conn.fetchval(sql_insert, email_lower)
            return token

    except Exception as e:
        await flatbed('exception', f"In subscribe_newsletter_ps: {e}")
        return "failed"


async def confirm_email_newsletter_ps(
        token: str
) -> bool:
    try:
        async with connection_context() as conn:
            sql_update = """
                UPDATE newsletter_emails
                SET is_verified = TRUE
                where token = $1
            """

            await conn.execute(sql_update, token)
            return True
    except Exception as e:
        await flatbed('exception', f"In confirm_email_newsletter_ps: {e}")
        return False


async def unsubscribe_newsletter_ps(
        token: str
) -> bool:
    try:
        async with connection_context() as conn:
            sql_delete = """
                DELETE FROM newsletter_emails
                WHERE token = $1
            """

            await conn.execute(sql_delete, token)
            return True
    except Exception as e:
        await flatbed('exception', f"In unsubscribe_newsletter_ps: {e}")
        return False
