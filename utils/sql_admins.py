from datetime import datetime, timedelta, date

from .logger import flatbed
from utils.conn import connection_context
from utils.hasher import check_password


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


#   Change with async with connection_context() as conn: from here on
async def get_users_data(username):
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow("""
                               SELECT user_id, full_name, level FROM users
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


async def get_dashboard_data_ps():
    """
    Retrieve dashboard data.

    Returns:
    - .
    """
    try:
        async with connection_context() as conn:
            # query = "SELECT * FROM get_dashboard_data();"
            # data = await conn.fetchrow(query)
            dashboard_data = {
                "totalBills": 404,
                "billsCompleted": 404,
                "billsPending": 404,
                "totalProducts": 404
            }
            return dashboard_data

    except Exception as e:
        await flatbed('exception', f"In get_dashboard_data_ps: {e}")
        raise RuntimeError(f"Failed to get dashboard data: {e}")


async def search_recent_activities_list(_date):
    """
    Retrieve recent activities list and filter with date range.

    Parameters:
    - _date (int): Date range filter index ('last week', 'last month', 'last year', 'last day').

    Returns:
    - List of records from the admins_records table that match the criteria.
    """

    query = "SELECT id, date, username, action FROM admins_records WHERE 1=1"
    params = []

    date_range = get_date_range(_date)

    if date_range:
        start_date, end_date = date_range
        query += " AND date >= $1 AND date <= $2"
        params.extend([start_date, end_date])

    limit = {0: 10, 1: 20, 2: 30}.get(_date)
    if limit:
        query += f" ORDER BY date DESC LIMIT {limit}"
    else:
        query += " ORDER BY date DESC"

    try:
        async with connection_context() as conn:
            return await conn.fetch(query, *params)
    except Exception as e:
        await flatbed('exception', f"In search_recent_activities_list: {e}")
        raise RuntimeError(f"Failed to search_recent_activities_list: {e}")


def get_date_range(_date: int):
    """
    Calculate the date range based on the `date` parameter.

    Parameters:
    - date (int): The date filter options index (e.g., 'Today', 'Last 7 days', 'Last 30 days', 'All').

    Returns:
    - Tuple of (start_date, end_date) if the date is valid; otherwise, returns None.
    """
    end_date = datetime.now()  # Current date and time

    if _date == 0:
        start_date = end_date - timedelta(days=1)
    elif _date == 1:
        start_date = end_date - timedelta(days=7)
    elif _date == 2:
        start_date = end_date - timedelta(days=30)  # Approximate 1 month as 30 days
    elif _date == 3:
        start_date = end_date - timedelta(days=365)  # Example: Last year
    else:
        return None  # Invalid date parameter, return None

    return start_date, end_date


async def get_users_list_ps():
    """
    Retrieve all users from users table.

    Returns:
    - All users from the users table.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT full_name, username, level FROM users;"
            users_list = await conn.fetch(query)
            return users_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In get_users_list_ps: {e}")
        raise RuntimeError(f"Failed to get users list: {e}")


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


async def search_products_list(search_query, search_by):
    """
    Retrieve products list based on a search query and filter with search_by.

    Parameters:
    - search_query (str): The term to search within the specified field.
    - search_by (int): The field to search in (0 for 'code', 1 for 'name'). Defaults to 'name' if not recognized.

    Returns:
    - List of records from the products table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_products_list($1, $2);"
            products_list = await conn.fetch(query, search_query, search_by)
            return products_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_products_list: {e}")
        raise RuntimeError(f"Failed to search products: {e}")


async def search_bills_list(search_query, search_by):
    """
    Retrieve bills list based on a search query and filter with search_by.

    Parameters:
    - search_query (str): The term to search within the specified field.
    - search_by (int): The field to search in:
        0 for 'bill_code',
        1 for 'customer_name',
        2 for 'customer_number'.

    Returns:
    - List of records from the bills table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_bills_list($1, $2);"
            bills_list = await conn.fetch(query, search_query, search_by)
            return bills_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_bills_list: {e}")
        raise RuntimeError(f"Failed to search bills: {e}")


async def search_bills_list_filtered(_date, state):
    """
    Retrieve bills list based on a date or state filter.

    Parameters:
    - date (int): The date filter for bills list.
    - state (int): The index for the state of the bill:

    Returns:
    - List of records from the bills table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_bills_list_filtered($1, $2);"
            bills_list = await conn.fetch(query, _date, state)
            return bills_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_bills_list_filtered: {e}")
        raise RuntimeError(f"Failed to search bills: {e}")


async def search_expenses_list_filtered(_date, category):
    """
    Retrieve expenses list based on a date or type filter.

    Parameters:
    - date (int): The date filter for expenses list.
    - category (int): The index for the category of the expense:

    Returns:
    - List of records from the expenses table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_expenses_list_filtered($1, $2);"
            expenses_list = await conn.fetch(query, _date, category)
            return expenses_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_expenses_list_filtered: {e}")
        raise RuntimeError(f"Failed to search expenses: {e}")


async def search_products_list_filtered(_date, category):
    """
    Retrieve products list based on a date or category filter.

    Parameters:
    - date (int): The date filter for products list.
    - category (int): The index for the type of the category:

    Returns:
    - List of records from the products table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_products_list_filtered($1, $2);"
            expenses_list = await conn.fetch(query, _date, category)
            return expenses_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_products_list_filtered: {e}")
        raise RuntimeError(f"Failed to search products: {e}")


async def search_rolls_for_product(product_code):
    """
    Retrieve rolls list based on product_code.

    Parameters:
    - product_code (str): The code for the product to which the rolls belong.

    Returns:
    - List of records from the rolls table that match the product code.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT product_code, roll_code, quantity, color 
            FROM public.rolls
            WHERE product_code = $1
            """
            rolls_list = await conn.fetch(query, product_code)
            return rolls_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_rolls_for_product: {e}")
        raise RuntimeError(f"Failed to search rolls: {e}")


async def get_image_for_product(code):
    """
    Retrieve the image for a given product based on its product code.

    Parameters:
    - code (str): The product code.

    Returns:
    - The image (bytes) if found, otherwise None.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT image FROM products
            WHERE product_code = $1
            """
            product_image = await conn.fetchval(query, code)  # fetchval() returns a single column value

            return product_image  # Returns the image bytes or None if not found

    except Exception as e:
        await flatbed('exception', f"In get_image_for_product: {e}")
        raise RuntimeError(f"Failed to retrieve image: {e}")


async def get_image_for_user(username):
    """
    Retrieve the image for a given username.

    Parameters:
    - username (str): Username for user.

    Returns:
    - The image (bytes) if found, otherwise None.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT photo FROM users
            WHERE username = $1
            """
            user_image = await conn.fetchval(query, username)  # fetchval() returns a single column value

            return user_image  # Returns the image bytes or None if not found

    except Exception as e:
        await flatbed('exception', f"In get_image_for_user: {e}")
        raise RuntimeError(f"Failed to retrieve image: {e}")


async def get_sample_image_for_roll(roll_code):
    """
    Retrieve the sample image for a given roll based on its roll code.

    Parameters:
    - roll_code (str): The roll code.

    Returns:
    - The image (bytes) if found, otherwise None.
    """
    try:
        async with connection_context() as conn:
            query = """
            SELECT sample_image FROM rolls
            WHERE roll_code = $1
            """
            sample_image = await conn.fetchval(query, roll_code)  # fetchval() returns a single column value

            return sample_image  # Returns the image bytes or None if not found

    except Exception as e:
        await flatbed('exception', f"In get_sample_image_for_roll: {e}")
        raise RuntimeError(f"Failed to retrieve sample image: {e}")


async def get_product_and_roll_ps(code):
    try:
        async with connection_context() as conn:
            upper_code = code.upper()
            if "R" in upper_code:
                product_code, roll_code = upper_code.split("R", 1)
                roll_code = f"R{roll_code}"
            else:
                product_code, roll_code = upper_code, None

            # Fetch the product
            query_product = "SELECT * FROM search_products_list($1, 0, 1, true);"
            product = await conn.fetchrow(query_product, product_code)

            if not product:
                return None

            # asyncpg returns a dictionary-like object, so we use column names directly
            product_dict = make_product_dic(product)

            # Fetch the specific roll
            if roll_code:
                query_roll = """
                    SELECT product_code, roll_code, quantity, color FROM rolls
                    WHERE product_code = $1 AND roll_code = $2
                """
                roll = await conn.fetchrow(query_roll, product_code, roll_code)

                if roll:
                    roll_dict = make_roll_dic(roll)
                    product_dict["rollsList"].append(roll_dict)

            return product_dict

    except Exception as e:
        await flatbed('exception', f"In get_product_and_roll_ps: {e}")
        return None


#  Helper
def make_bill_dic(data):
    bill = {
        "billCode": data["bill_code"],
        "billDate": data["bill_date"].isoformat() if isinstance(data["bill_date"],
                                                                (date, datetime)) else data["bill_date"],
        "dueDate": data["due_date"].isoformat() if isinstance(data["due_date"],
                                                              (date, datetime)) else data["due_date"],
        "customerName": data["customer_name"],
        "customerNumber": data["customer_number"],
        "price": data["price"],
        "paid": data["paid"],
        "remaining": data["remaining"],
        "fabrics": data["fabrics"],
        "parts": data["parts"],
        "status": data["status"],
        "salesman": data["salesman"],
        "tailor": data["tailor"],
        "additionalData": data["additional_data"],
        "installation": data["installation"]
    }
    return bill


def make_expense_dic(data):
    expense = {
        "id": data["id"],
        "categoryIndex": data["category_index"],
        "description": data["description"],
        "amount": data["amount"],
        "date": data["date"].isoformat() if isinstance(data["date"],
                                                       (date, datetime)) else data["date"]
    }
    return expense


def make_product_dic(data):
    product = {
        "productCode": data["product_code"],
        "name": data["name"],
        "categoryIndex": data["category"],
        "quantityInCm": data["quantity"],
        "costPerMetre": data["cost_per_metre"],
        "pricePerMetre": data["price_per_metre"],
        "description": data["description"],
        "rollsList": []
    }
    return product


def make_roll_dic(data):
    roll = {
        "productCode": data["product_code"],
        "rollCode": data["roll_code"],
        "quantityInCm": data["quantity"],
        "colorLetter": data["color"]
    }
    return roll


async def get_bill_ps(code):
    """
    Retrieve bill based on code (Async Version for asyncpg).

    Parameters:
    - code (str): The code for the specified bill.

    Returns:
    - dict: A single bill.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_bills_list($1, $2, 1, true);"
            data = await conn.fetchrow(query, code, 0)

            if data:
                bill = make_bill_dic(data)
                return bill

            return None

    except Exception as e:
        await flatbed('exception', f"In get_bill_ps: {e}")
        return None


async def remove_product_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM products WHERE product_code = $1", code)
    except Exception as e:
        await flatbed('exception', f"in remove_product_ps: {e}")


async def remove_roll_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM rolls WHERE roll_code = $1", code)
    except Exception as e:
        await flatbed('exception', f"in remove_roll_ps: {e}")


async def remove_bill_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM bills WHERE bill_code = $1", code)
    except Exception as e:
        await flatbed('exception', f"in remove_bill_ps: {e}")


async def remove_user_ps(username):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM users WHERE username = $1", username)
    except Exception as e:
        await flatbed('exception', f"in remove_user_ps: {e}")
