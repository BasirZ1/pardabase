from typing import Optional

from .hasher import hash_password
from .logger import flatbed
from utils.conn import get_connection, release_connection


async def insert_new_product(image, name, category_index, cost_per_metre, price, description):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO products (
                image,
                name,
                category,
                cost_per_metre,
                price_per_metre,
                description
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING product_code
        """
        product_code = await conn.fetchval(sql_insert, image, name, category_index, cost_per_metre, price, description)
        return product_code
    except Exception as e:
        await flatbed('exception', f"In insert_new_product: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_product(codeToEdit, image, name, category_index, cost_per_metre, price, description):
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE products
            SET image = $1, name = $2,
            category = $3, cost_per_metre = $4,
            price_per_metre = $5, description = $6
            WHERE product_code = $7
            RETURNING product_code
        """
        product_code = await conn.fetchval(sql_update, image, name,
                                           category_index, cost_per_metre, price, description, codeToEdit)

        return product_code is not None
    except Exception as e:
        await flatbed('exception', f"in update_product: {e}")
        return False
    finally:
        await release_connection(conn)


async def update_roll_quantity_ps(roll_code, quantity, action):
    if action not in ["subtract", "add"]:
        await flatbed('error', f"Invalid action: {action}. Expected 'subtract' or 'add'.")
        return False

    conn = await get_connection()
    try:
        # Using Python logic instead of relying on PostgreSQL CASE
        quantity = -quantity if action == "subtract" else quantity

        sql_update = """
                    UPDATE rolls
                    SET quantity = quantity + $1
                    WHERE roll_code = $2
                    RETURNING quantity
                """
        updated_quantity = await conn.fetchval(sql_update, quantity, roll_code)

        return updated_quantity is not None

    except Exception as e:
        await flatbed('exception', f"In update_roll_quantity_ps: {e}")
        return False
    finally:
        await release_connection(conn)


async def add_expense_ps(category_index, description, amount):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO expenses (category_index, description, amount)
            VALUES ($1, $2, $3)
            RETURNING id;
        """
        expense_id = await conn.fetchval(sql_insert, category_index, description, amount)

        return expense_id
    except Exception as e:
        await flatbed('exception', f"In add_expense: {e}")
        return None
    finally:
        await release_connection(conn)


async def insert_new_roll(product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO rolls (
                product_code,
                quantity,
                color,
                sample_image
            ) VALUES ($1, $2, $3, $4)
            RETURNING roll_code
        """
        roll_code = await conn.fetchval(sql_insert, product_code, quantity, color_letter, image_data)

        return f"{product_code}{roll_code}" if roll_code else None
    except Exception as e:
        await flatbed('exception', f"In insert_new_roll: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_roll(codeToEdit, product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE rolls
            SET quantity = $1,
                color = $2,
                sample_image = $3
            WHERE roll_code = $4
        """
        await conn.execute(sql_update, quantity, color_letter, image_data, codeToEdit)

        return f"{product_code}{codeToEdit}"
    except Exception as e:
        await flatbed('exception', f"In update_roll: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_user(usernameToEdit: str, full_name: str, user_name: str,
                      level: int, password: Optional[str] = None, image_data: Optional[bytes] = None):
    """
    Updates user details in the database.

    Args:
        usernameToEdit (str): The username of the user to be updated.
        full_name (str): The new full name of the user.
        user_name (str): The new username.
        level (int): The new access level.
        password (Optional[str]): The new password (hashed before storage) or None to keep the existing one.
        image_data (Optional[bytes]): The new profile photo or None to keep the existing one.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    conn = await get_connection()
    try:

        # Base query
        update_fields = ["full_name = $1", "username = $2, level = $3, photo = $4"]
        values = [full_name, user_name, level, image_data]

        # Conditional updates
        index = 5  # Start at $5
        if password:
            update_fields.append(f"password = ${index}")
            values.append(hash_password(password))  # Hash password before storage
            index += 1

        values.append(usernameToEdit)  # WHERE condition

        sql_update = f"""
            UPDATE users
            SET {", ".join(update_fields)}
            WHERE username = ${index}
        """

        await conn.execute(sql_update, *values)
        return True

    except Exception as e:
        await flatbed('exception', f"In update_user: {e}")
        return False

    finally:
        await release_connection(conn)


async def add_new_user_ps(token, full_name, username, password, level, photo):
    """
    Adds a new user to the database.

    Args:
        token (str): The login token for the user.
        full_name (str): The full name of the user.
        username (str): The username of the user.
        password (str): The plain-text password for the user (will be hashed before storage).
        level (int): The access level of the user.
        photo (bytes | None): The photo for the user (can be None).

    Returns:
        bool: True if the user was added successfully, False otherwise.
    """
    conn = await get_connection()
    try:

        # Hash the password before storing it (ensure it's not async)
        hashed_password = hash_password(password)

        # Insert user into the table with explicit column names
        sql_insert = """
            INSERT INTO users (login_token, full_name, username, password, level, photo) 
            VALUES ($1, $2, LOWER($3), $4, $5, $6)
        """

        await conn.execute(sql_insert, token, full_name, username, hashed_password, level, photo)
        return True

    except Exception as e:
        await flatbed('exception', f"in add_new_user_ps: {e}")
        return False

    finally:
        await release_connection(conn)


async def insert_new_bill(
        bill_date: Optional[str] = None,
        due_date: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_number: Optional[str] = None,
        price: Optional[int] = None,
        paid: Optional[int] = None,
        remaining: Optional[int] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        status: Optional[str] = 'pending',
        salesman: Optional[str] = None,
        tailor: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO bills (
                bill_date,
                due_date,
                customer_name,
                customer_number,
                price,
                paid,
                remaining,
                fabrics,
                parts,
                status,
                salesman,
                tailor,
                additional_data,
                installation
            ) VALUES ($1::DATE, $2::DATE, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12, $13::jsonb, $14)
            RETURNING bill_code
        """

        bill_code = await conn.fetchval(
            sql_insert,
            bill_date,
            due_date,
            customer_name,
            customer_number,
            price,
            paid,
            remaining,
            fabrics,
            parts,
            status,
            salesman,
            tailor,
            additional_data,
            installation
        )
        return bill_code
    except Exception as e:
        await flatbed('exception', f"In insert_new_bill: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_bill(
        bill_code: str,
        due_date: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_number: Optional[str] = None,
        price: Optional[int] = None,
        paid: Optional[int] = None,
        remaining: Optional[int] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET due_date = $1::DATE,
                customer_name = $2,
                customer_number = $3,
                price = $4,
                paid = $5,
                remaining = $6,
                fabrics = $7::jsonb,
                parts = $8::jsonb,
                additional_data = $9::jsonb,
                installation = $10,
                updated_at = NOW()
            WHERE bill_code = $11
        """
        await conn.execute(
            sql_update,
            due_date,
            customer_name,
            customer_number,
            price,
            paid,
            remaining,
            fabrics,
            parts,
            additional_data,
            installation,
            bill_code
        )
        return bill_code
    except Exception as e:
        await flatbed('exception', f"In update_bill: {e}")
        return None
    finally:
        await release_connection(conn)


async def update_bill_status_ps(bill_code: str, status: str) -> bool:
    """
    Update a bill's status in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        status (str): The new status for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET status = $1
            WHERE bill_code = $2
            RETURNING status
        """
        updated_status = await conn.fetchval(sql_update, status, bill_code)

        return updated_status is not None
    except Exception as e:
        await flatbed('exception', f"In update_bill_status_ps: {e}")
        return False
    finally:
        await release_connection(conn)


async def update_bill_tailor_ps(bill_code: str, tailor: str) -> bool:
    """
    Update a bill's tailor in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        tailor (str): The tailor for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET tailor = $1
            WHERE bill_code = $2
            RETURNING tailor
        """
        updated_tailor = await conn.fetchval(sql_update, tailor, bill_code)

        return updated_tailor is not None
    except Exception as e:
        await flatbed('exception', f"In update_bill_tailor_ps: {e}")
        return False
    finally:
        await release_connection(conn)


async def add_payment_bill_ps(bill_code: str, amount: int) -> bool:
    """
    Update a bill's payment in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        amount (int): The amount added as payment for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = await get_connection()
    try:
        sql_query = "CALL update_bill_payment($1, $2);"

        await conn.execute(sql_query, bill_code, amount)
        return True  # If execution reaches here, the update was successful
    except Exception as e:
        await flatbed('exception', f"In add_payment_bill_ps: {e}")
        return False
    finally:
        await release_connection(conn)


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
    conn = await get_connection()
    try:
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
    finally:
        await release_connection(conn)


async def subscribe_newsletter_ps(
        email: str
) -> str:
    conn = await get_connection()
    try:
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
    finally:
        await release_connection(conn)


async def confirm_email_newsletter_ps(
        token: str
) -> bool:
    conn = await get_connection()
    try:
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
    finally:
        await release_connection(conn)


async def unsubscribe_newsletter_ps(
        token: str
) -> bool:
    conn = await get_connection()
    try:
        sql_delete = """
            DELETE FROM newsletter_emails
            WHERE token = $1
        """

        await conn.execute(sql_delete, token)
        return True
    except Exception as e:
        await flatbed('exception', f"In unsubscribe_newsletter_ps: {e}")
        return False
    finally:
        await release_connection(conn)
