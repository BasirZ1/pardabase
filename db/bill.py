import datetime
from typing import Optional

from helpers import make_bill_dic
from utils import flatbed
from utils.conn import connection_context


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
        salesman: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    try:
        async with connection_context() as conn:
            # Convert bill_date and due_date from string to date if provided
            if bill_date:
                bill_date = datetime.datetime.strptime(bill_date, "%Y-%m-%d").date() if isinstance(bill_date,
                                                                                                   str) else bill_date
            if due_date:
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date() if isinstance(due_date,
                                                                                                 str) else due_date

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
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12, $13::jsonb, $14)
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
                "pending",
                salesman,
                None,
                additional_data,
                installation
            )
            return bill_code
    except Exception as e:
        await flatbed('exception', f"In insert_new_bill: {e}")
        return None


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
    try:
        async with connection_context() as conn:
            if due_date:
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date() if isinstance(due_date,
                                                                                                 str) else due_date

            sql_update = """
                UPDATE bills
                SET due_date = $1,
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


async def update_bill_status_ps(bill_code: str, status: str) -> bool:
    """
    Update a bill's status in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        status (str): The new status for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    try:
        async with connection_context() as conn:
            sql_update = """
                UPDATE bills
                SET status = $1,
                updated_at = now()
                WHERE bill_code = $2
                RETURNING status
            """
            updated_status = await conn.fetchval(sql_update, status, bill_code)

            return updated_status is not None
    except Exception as e:
        await flatbed('exception', f"In update_bill_status_ps: {e}")
        raise e


async def update_bill_tailor_ps(bill_code: str, tailor: str) -> bool:
    """
    Update a bill's tailor in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        tailor (str): The tailor for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """

    try:
        async with connection_context() as conn:
            sql_update = """
                UPDATE bills
                SET tailor = $1,
                updated_at = now()
                WHERE bill_code = $2
                RETURNING tailor
            """
            updated_tailor = await conn.fetchval(sql_update, tailor, bill_code)

            return updated_tailor is not None
    except Exception as e:
        await flatbed('exception', f"In update_bill_tailor_ps: {e}")
        raise e


async def add_payment_bill_ps(bill_code: str, amount: int) -> bool:
    """
    Update a bill's payment in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        amount (int): The amount added as payment for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    try:
        async with connection_context() as conn:
            sql_query = "CALL update_bill_payment($1, $2);"

            await conn.execute(sql_query, bill_code, amount)
            return True  # If execution reaches here, the update was successful
    except Exception as e:
        await flatbed('exception', f"In add_payment_bill_ps: {e}")
        return False


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


async def remove_bill_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM bills WHERE bill_code = $1", code)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_bill_ps: {e}")
        return False
