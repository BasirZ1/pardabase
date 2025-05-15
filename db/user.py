from typing import Optional

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
        bool: True if the user was added successfully, False otherwise.
    """

    try:
        async with connection_context() as conn:
            # Hash the password before storing it (ensure it's not async)
            hashed_password = hash_password(password)

            # Insert user into the table with explicit column names
            sql_insert = """
                INSERT INTO users (full_name, username, password, level) 
                VALUES ($1, LOWER($2), $3, $4)
            """

            await conn.execute(sql_insert, full_name, username, hashed_password, level)
            return True

    except Exception as e:
        await flatbed('exception', f"in add_new_user_ps: {e}")
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
        bool: True if the update was successful, False otherwise.
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
            """

            await conn.execute(sql_update, *values)
            return True

    except Exception as e:
        await flatbed('exception', f"In update_user: {e}")
        return False


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
        raise RuntimeError(f"Failed to check username and password: {e}")


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
        raise RuntimeError(f"Failed to get users data: {e}")


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
        raise RuntimeError(f"Failed to update users password: {e}")


async def get_users_list_ps():
    """
    Retrieve all users from users table.

    Returns:
    - All users from the users table.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT full_name, username, level, image_url FROM users;"
            users_list = await conn.fetch(query)
            return users_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In get_users_list_ps: {e}")
        raise RuntimeError(f"Failed to get users list: {e}")


async def remove_user_ps(username):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM users WHERE username = $1", username)
    except Exception as e:
        await flatbed('exception', f"in remove_user_ps: {e}")


async def remember_users_action(username, action):
    """
        Remember admins action
        :param username: username associated with the user.
        :param action: action performed by the user.
    """
    # SQL query to
    sql_insert = """
            INSERT INTO admins_records (
                username,
                action
            ) VALUES ($1, $2)
        """
    try:
        async with connection_context() as conn:
            await conn.execute(sql_insert, username, action)
    except Exception as e:
        await flatbed('exception', f"In remember_users_action: {e}")
        raise RuntimeError(f"Failed to remember users action: {e}")
