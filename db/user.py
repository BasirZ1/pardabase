import uuid
from typing import Optional

from helpers import make_employment_info_dic, make_profile_data_dic, parse_date
from utils import flatbed
from utils.conn import connection_context
from utils.hasher import hash_password, check_password


async def insert_new_user(full_name, username, password, level):
    """
    Adds a new user to the database.

    Args:
        full_name (str): The full name of the user.
        username (str): The username of the user.
        password (str): The plain-text password for the user (will be hashed before storage).
        level (int): The access level of the user.

    Returns:
        user_id: user_id if the user was added successfully, None otherwise.
    """

    try:
        async with connection_context() as conn:
            # Hash the password before storing it (ensure it's not async)
            hashed_password = hash_password(password)

            user_id = await conn.fetchval(
                "SELECT add_new_user_procedure($1, $2, $3, $4)",
                full_name,
                username,
                hashed_password,
                level
            )

            return user_id

    except Exception as e:
        await flatbed('exception', f"in insert_new_user: {e}")
        return False


async def update_user(usernameToEdit: str, full_name: str, user_name: str,
                      level: int, password: Optional[str] = None):
    """
    Updates user details in the database.

    Args:
        usernameToEdit (str): The username of the user to be updated.
        full_name (str): The new full name of the user.
        user_name (str): The new username.
        level (int): The new access level.
        password (Optional[str]): The new password (hashed before storage) or None to keep the existing one.

    Returns:
        user_id: user_id if the update was successful, None otherwise.
    """
    try:
        async with connection_context() as conn:
            # Base query
            update_fields = ["full_name = $1", "username = $2, level = $3"]
            values = [full_name, user_name, level]

            # Conditional updates
            index = 4  # Start at $4
            if password:
                update_fields.append(f"password = ${index}")
                values.append(hash_password(password))  # Hash password before storage
                index += 1

            values.append(usernameToEdit)  # WHERE condition

            sql_update = f"""
                UPDATE users
                SET {", ".join(update_fields)}
                WHERE username = ${index}
                RETURNING user_id::text
            """

            user_id = await conn.fetchval(sql_update, *values)
            return user_id

    except Exception as e:
        await flatbed('exception', f"In update_user: {e}")
        return None


async def edit_employment_info_ps(
        user_id: str,
        salary_amount: Optional[int] = None,
        salary_start_date: Optional[str] = None,
        salary_cycle: Optional[str] = None,
        tailor_type: Optional[str] = None,
        salesman_status: Optional[str] = None,
        bill_bonus_percent: Optional[int] = None,
        note: Optional[str] = None,
        is_active: Optional[bool] = None
):
    """
    Updates employment info in the database.

    Args:
        user_id (str): The user_id for editing the employment info.
        salary_amount (Optional[int]): The salary amount of the employee.
        salary_start_date (Optional[str]): The salary start date of the employee.
        salary_cycle (Optional[str]): The cycle of salary of the employee (monthly, weekly).
        tailor_type (Optional[str]): The tailor type of the employee.
        salesman_status (Optional[str]): The salesman status of the employee.
        bill_bonus_percent (Optional[int]): Bill bonus percentage if any.
        note (Optional[str]): Detail note.
        is_active (Optional[bool]): Is Active (Toggle user as active or inactive).

    Returns:
        str: username if the update was successful, None otherwise.
    """
    try:
        async with (connection_context() as conn):
            if salary_start_date:
                salary_start_date = parse_date(salary_start_date)

            sql_update = """
                WITH updated AS (
                    UPDATE user_employment_info
                    SET salary_amount = $1,
                        salary_start_date = $2,
                        tailor_type = $3,
                        salesman_status = $4,
                        bill_bonus_percent = $5,
                        note = $6,
                        salary_cycle = $7,
                        is_active = $8
                    WHERE user_id = $9
                    RETURNING user_id
                )
                SELECT u.username
                FROM updated
                JOIN users u ON u.user_id = updated.user_id;
            """

            username = await conn.fetchval(sql_update, salary_amount, salary_start_date, tailor_type,
                                           salesman_status, bill_bonus_percent, note, salary_cycle, is_active, user_id)
            return username

    except Exception as e:
        await flatbed('exception', f"In edit_employment_info_ps: {e}")
        return None


async def check_username_password(username, password):
    """
    Validates a user's username and password by checking against the database.

    Args:
        username (str): The username provided by the admin.
        password (str): The password provided by the admin.

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """
    try:
        async with connection_context() as conn:
            stored_password = await conn.fetchval("""
                    SELECT password FROM users
                    WHERE username = lower($1)
                """, username)

            if stored_password:
                # Check the provided password against the stored hash
                return check_password(stored_password, password)
            return False

    except Exception as e:
        await flatbed('exception', f"In check_username_password: {e}")
        raise


async def check_username_and_set_chat_id(username: str, chat_id: int):
    """
        Validates a user's username and sets chat_id for the user.

        Args:
            username (str): The username provided by the user.
            chat_id (int): The chat_id for the user.

        Returns:
            bool: True if the username was valid, False otherwise.
        """
    try:
        async with connection_context() as conn:
            stored_user_id = await conn.fetchval("""
                SELECT user_id FROM users WHERE username = lower($1)
            """, username)

            if not stored_user_id:
                return False  # Username not found, abort.

            await conn.execute("""
                UPDATE users SET telegram_id = $1 WHERE user_id = $2
            """, chat_id, stored_user_id)

            return True
    except Exception as e:
        await flatbed('exception', f"In check_username_and_set_chat_id: {e}")
        return False


async def get_users_data(username):
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow("""
                               SELECT user_id::varchar, full_name, level, image_url FROM users
                               WHERE username = lower($1)
                           """, username)
            return data if data else None
    except Exception as e:
        await flatbed('exception', f"In get_users_data: {e}")
        raise


async def get_employment_info_ps(user_id):
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow("""
                               SELECT id, user_id::TEXT, salary_amount, salary_start_date, tailor_type, salesman_status,
                                bill_bonus_percent, note, salary_cycle, last_calculated_date, is_active 
                                FROM user_employment_info
                               WHERE user_id = $1
                           """, user_id)
            if not data:
                return None

            employment_info = make_employment_info_dic(data)
            return employment_info

    except Exception as e:
        await flatbed('exception', f"In get_employment_info_ps: {e}")
        raise


async def get_profile_data_ps(user_id: str):
    """
    Fetches the total earnings and total withdrawals for a given user from the database.

    Parameters:
    ----------
    user_id : str
        The UUID of the user as a string. This will be validated and cast to UUID type.

    Returns:
    -------
    dict or None
        A dictionary containing 'total_earnings' and 'total_withdrawals' if the user exists.
        Returns None if no data is found for the given user_id.
    """
    try:
        async with connection_context() as conn:

            user_id = uuid.UUID(user_id)
            data = await conn.fetchrow("""
                SELECT * FROM get_profile_data($1);
                           """, user_id)
            if not data:
                return None

            profile_data = make_profile_data_dic(data)
            return profile_data

    except Exception as e:
        await flatbed('exception', f"In get_profile_data_ps: {e}")
        raise


async def update_users_password(username, new_password):
    try:
        async with connection_context() as conn:
            await conn.execute("""
            UPDATE users
            SET password = $1
            WHERE username = lower($2)
        """, new_password, username)
    except Exception as e:
        await flatbed('exception', f"In update_users_password: {e}")
        raise


async def get_users_list_ps():
    """
    Retrieve all users from users table.

    Returns:
    - All users from the users table.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT user_id::TEXT, full_name, username, level, image_url FROM users;"
            users_list = await conn.fetch(query)
            return users_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In get_users_list_ps: {e}")
        raise


async def get_emails_high_clearance_users_ps():
    """
    Retrieve all emails from users table for high clearance users.

    Returns:
        List of email strings for high clearance users.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT email_address FROM users WHERE level > 2;"
            records = await conn.fetch(query)
            emails_list = [r['email_address'] for r in records]  # extract email field
            return emails_list

    except Exception as e:
        await flatbed('exception', f"In get_emails_high_clearance_users_ps: {e}")
        raise


async def remove_user_ps(username):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM users WHERE username = $1", username)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_user_ps: {e}")
        return False


async def remember_users_action(user_id, action):
    """
        Remember users action
        :param user_id: user_id associated with the user.
        :param action: action performed by the user.
    """
    # SQL query to
    sql_insert = """
            INSERT INTO user_actions (
                user_id,
                action
            ) VALUES ($1, $2)
        """
    try:
        async with connection_context() as conn:
            await conn.execute(sql_insert, user_id, action)
    except Exception as e:
        await flatbed('exception', f"In remember_users_action: {e}")
        raise
