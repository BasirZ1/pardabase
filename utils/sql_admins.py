from datetime import datetime, timedelta

from .logger import flatbed
from utils.conn import get_connection
from utils.hasher import check_password, hash_password


def check_admins_token(level, token):
    """
    Function to check the administrator's token and level against the database.
    """
    query = """
            SELECT 1 FROM admins
            WHERE login_token = %s AND level >= %s
            LIMIT 1
            """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (token, level))
            return cur.fetchone() is not None


def check_username_password_admins(username, password):
    """
    Validates an admin's username and password by checking against the database.

    Args:
        username (str): The username provided by the admin.
        password (str): The password provided by the admin.

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT password FROM admins
                WHERE username ILIKE %s
            """, (username,))

            stored_password = cur.fetchone()

        if stored_password:
            # Check the provided password against the stored hash
            return check_password(stored_password[0], password)
        return False
    finally:
        conn.close()


def get_admins_data(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT login_token, full_name, level FROM admins
                WHERE username ILIKE %s
            """, (username,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    if data:
        return data
    else:
        return None


def update_admins_password(username, new_password):
    conn = get_connection()
    cur = conn.cursor()

    sql_update = f"""
                UPDATE admins
                SET password = %s
                WHERE username ILIKE %s
            """
    values = (
        new_password,
        username
    )

    cur.execute(sql_update, values)
    conn.commit()
    cur.close()
    conn.close()


def search_recent_activities_list(date):
    """
    Retrieve recent activities list and filter with date range.

    Parameters:
    - date (int): Date range filter index ('last week', 'last month', 'last year', 'last day').

    Returns:
    - List of tuples representing rows from the admins_records table that match the criteria.
    """

    # Establish database connection
    conn = get_connection()
    cur = conn.cursor()

    # Base query for retrieving logs data
    query = (f"SELECT id, date, username, action "
             f"FROM admins_records WHERE 1=1")

    # List to hold query parameters
    params = []

    # Calculate date range based on `date` parameter
    date_range = get_date_range(date)

    limit = None

    if date == 0:
        limit = 10
    elif date == 1:
        limit = 20
    elif date == 2:
        limit = 30

    # Add date filter to the query if a valid date range is determined
    if date_range:
        start_date, end_date = date_range
        query += " AND date >= %s AND date <= %s"
        if limit is not None:
            query += f"  LIMIT {limit} "
        params.extend([start_date, end_date])

    # Execute the query with the constructed parameters
    cur.execute(query, tuple(params))

    # Fetch all matching rows
    recent_activity_list = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    return recent_activity_list


def get_date_range(date: int):
    """
    Calculate the date range based on the `date` parameter.

    Parameters:
    - date (int): The date filter options index (e.g., 'Today', 'Last 7 days', 'Last 30 days', 'All').

    Returns:
    - Tuple of (start_date, end_date) if the date is valid; otherwise, returns None.
    """
    end_date = datetime.now()  # Current date and time

    if date == 0:
        start_date = end_date - timedelta(days=1)
    elif date == 1:
        start_date = end_date - timedelta(days=7)
    elif date == 2:
        start_date = end_date - timedelta(days=30)  # Approximate 1 month as 30 days
    elif date == 3:
        start_date = end_date - timedelta(days=365)  # Example: Last year
    else:
        return None  # Invalid date parameter, return None

    return start_date, end_date


def remember_admins_action(admin_name, action):
    """
        Remember admins action
        :param admin_name: username associated with the admin.
        :param action: action performed by the admin.
    """
    conn = get_connection()
    cur = conn.cursor()

    # SQL query to
    sql_insert = """
            INSERT INTO admins_records (
                username,
                action
            ) VALUES (%s, %s)
        """
    values = (
        admin_name,
        action,
    )

    cur.execute(sql_insert, values)
    conn.commit()
    cur.close()
    conn.close()


def add_new_admin_ps(token, full_name, username, password, level):
    """
    Adds a new admin to the database.

    Args:
        token (str): The login token for the admin.
        full_name (str): The full name of the admin.
        username (str): The username of the admin.
        password (str): The plain-text password for the admin (will be hashed before storage).
        level (int): The access level of the admin.

    Returns:
        bool: True if the admin was added successfully, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Hash the password before storing it
            hashed_password = hash_password(password)

            # SQL query to insert the admin
            sql_insert = """
                INSERT INTO admins (
                    login_token,
                    full_name,
                    username,
                    password,
                    level
                ) VALUES (%s, %s, LOWER(%s), %s, %s)
            """
            values = (
                token,
                full_name,
                username,
                hashed_password,  # Store the hashed password
                level
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error adding new admin: {e}")
        return False
    finally:
        conn.close()


def search_products_list(search_query, search_by):
    """
    Retrieve products list based on a search query and filter with search_by.

    Parameters:
    - search_query (str): The term to search within the specified field.
    - search_by (int): The field to search in (0 for 'code', 1 for 'name'). Defaults to 'name' if not recognized.

    Returns:
    - List of tuples representing rows from the inventory table that match the criteria.
    """
    # Establish database connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Base query for retrieving product data
            query = (
                "SELECT code, name, category, quantity_in_cm, price_per_metre, description, color "
                "FROM inventory WHERE 1=1"
            )

            # List to hold query parameters
            params = []

            # Add search conditions based on `search_by` field
            if search_query:
                search_fields = {
                    0: 'code',
                    1: 'name'
                }

                # Validate `search_by` field, default to `name` if not recognized
                column_to_search = search_fields.get(search_by, 'name')

                # Log a warning for invalid `search_by` values
                if search_by not in search_fields:
                    flatbed('warning', f"Invalid search_by value: {search_by}. Defaulting to 'name'.")

                # Add case-insensitive partial match condition
                query += f" AND LOWER({column_to_search}) ILIKE %s"
                params.append(f"%{search_query}%")
            else:
                flatbed('warning', "Empty search_query provided. Returning empty results.")
                return []

            # Limit the result set to 20 items
            query += " LIMIT 20;"

            # Execute the query with parameters
            cur.execute(query, tuple(params))

            # Fetch all rows
            products_list = cur.fetchall()

        return products_list

    except Exception as e:
        flatbed('exception', f"In search_products_list: {e}")
        raise RuntimeError(f"Failed to search products: {e}")

    finally:
        conn.close()


def get_image_for_product(code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT image FROM inventory
                WHERE code = %s
            """, (code,))

    product_image = cur.fetchone()

    cur.close()
    conn.close()
    if product_image:
        return product_image[0]
    else:
        return None


def get_product_ps(code):
    """
        Retrieve product based on code.

        Parameters:
        - code (str): The code for the specified product.

        Returns:
        - Tuple: a single product.
        """
    # Establish database connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            cur.execute("""
                            SELECT code, name, category, quantity_in_cm, price_per_metre, description, color 
                            FROM inventory WHERE code = %s
                        """, (code,))

            # Fetch all rows
            product = cur.fetchone()

        return product

    except Exception as e:
        flatbed('exception', f"In get_product_ps: {e}")
        return None

    finally:
        conn.close()


def remove_product_ps(code):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Delete the driver profile
        cur.execute("""
            DELETE FROM inventory
            WHERE code = %s
        """, (code,))

        conn.commit()

    except Exception as e:
        # Roll back changes if any errors occur
        conn.rollback()
        flatbed('exception', f"Error removing product: {e}")

    finally:
        cur.close()
        conn.close()
