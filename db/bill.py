import datetime
import json
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

            payment_history = json.dumps([
                {
                    "type": "initial",
                    "price": price,
                    "paid": paid,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            ])

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
                    installation,
                    payment_history
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12, $13::jsonb, $14, $15::jsonb)
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
                installation,
                payment_history
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
        installation: Optional[str] = None,
        username: Optional[str] = None,
) -> Optional[str]:
    try:
        async with connection_context() as conn:
            # Fetch existing data
            row = await conn.fetchrow(
                "SELECT price, paid, payment_history FROM bills WHERE bill_code = $1", bill_code
            )

            if not row:
                return None

            old_price = row['price']
            old_paid = row['paid']
            history = row['payment_history'] or []

            # Build history updates
            now = datetime.datetime.now().isoformat()
            updates = []

            if price is not None and price != old_price:
                updates.append({
                    "type": "price_changed",
                    "price": price,
                    "old_price": old_price,
                    "edited_by": username,
                    "timestamp": now
                })

            if paid is not None and paid != old_paid:
                updates.append({
                    "type": "payment_edited",
                    "paid": paid,
                    "old_paid": old_paid,
                    "edited_by": username,
                    "timestamp": now
                })

            # Append to existing history
            new_history = history + updates if updates else history

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
                    payment_history = $11::jsonb,
                    updated_at = NOW()
                WHERE bill_code = $12
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
                new_history,
                bill_code,
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


async def add_payment_bill_ps(bill_code: str, amount: int, username: str) -> bool:
    """
    Update a bill's payment in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        amount (int): The amount added as payment for the bill.
        username (str): Collector of the payment for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    try:
        async with connection_context() as conn:
            sql_query = "CALL update_bill_payment($1, $2, $3);"

            await conn.execute(sql_query, bill_code, amount, username)
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


async def get_payment_history_ps(code):
    """
    Retrieve payment history based on code (Async Version for asyncpg).

    Parameters:
    - code (str): The code for the specified bill.

    Returns:
    - str: payment history.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT payment_history::TEXT from bills where bill_code = $1;"
            payment_history = await conn.fetchrow(query, code)

            if payment_history:
                return payment_history["payment_history"]

            return None

    except Exception as e:
        await flatbed('exception', f"In get_payment_history_ps: {e}")
        return None


async def remove_bill_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM bills WHERE bill_code = $1", code)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_bill_ps: {e}")
        return False
