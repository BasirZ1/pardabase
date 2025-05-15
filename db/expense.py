from utils import flatbed
from utils.conn import connection_context


async def add_expense_ps(category_index, description, amount):
    try:
        async with connection_context() as conn:
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
