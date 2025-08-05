import datetime
import json
from typing import Optional
from zoneinfo import ZoneInfo

from helpers import make_bill_dic, parse_date
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
        status: Optional[str] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        salesman: Optional[str] = None,
        tailor: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    try:
        async with connection_context() as conn:
            # Convert bill_date and due_date from string to date if provided
            if bill_date:
                bill_date = parse_date(bill_date)

            if due_date:
                due_date = parse_date(due_date)

            kabul_tz = ZoneInfo("Asia/Kabul")
            payment_history = json.dumps([
                {
                    "type": "initial",
                    "price": price,
                    "paid": paid,
                    "timestamp": datetime.datetime.now(kabul_tz).isoformat()
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
                    status,
                    fabrics,
                    parts,
                    salesman,
                    tailor,
                    additional_data,
                    installation,
                    payment_history
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10::jsonb, $11, $12, $13::jsonb, $14, $15::jsonb)
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
                status,
                fabrics,
                parts,
                salesman,
                tailor,
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
        status: Optional[str] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        salesman: Optional[str] = None,
        tailor: Optional[str] = None,
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
            history_raw = row['payment_history']
            history = json.loads(history_raw) if history_raw else []

            # Build history updates
            kabul_tz = ZoneInfo("Asia/Kabul")
            now = datetime.datetime.now(kabul_tz).isoformat()
            updates = []

            if price is not None and price != old_price:
                updates.append({
                    "type": "price_changed",
                    "from": old_price,
                    "to": price,
                    "edited_by": username,
                    "timestamp": now
                })

            if paid is not None and paid != old_paid:
                updates.append({
                    "type": "payment_edited",
                    "from": old_paid,
                    "to": paid,
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
                    status = $7,
                    fabrics = $8::jsonb,
                    parts = $9::jsonb,
                    salesman = $10,
                    tailor = $11,
                    additional_data = $12::jsonb,
                    installation = $13,
                    payment_history = $14::jsonb,
                    updated_at = NOW()
                WHERE bill_code = $15
            """
            await conn.execute(
                sql_update,
                due_date,
                customer_name,
                customer_number,
                price,
                paid,
                remaining,
                status,
                fabrics,
                parts,
                salesman,
                tailor,
                additional_data,
                installation,
                json.dumps(new_history),
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


async def update_bill_tailor_ps(bill_code: str, tailor: str) -> Optional[str]:
    """
    Update a bill's tailor in the bills table and return the updated tailor's full name.
    """
    try:
        async with connection_context() as conn:
            sql_update = """
                WITH updated_bill AS (
                    UPDATE bills
                    SET tailor = $1,
                        updated_at = now()
                    WHERE bill_code = $2
                    RETURNING tailor
                )
                SELECT 
                    COALESCE(u.full_name, ub.tailor) AS tailor_full_name
                FROM updated_bill ub
                LEFT JOIN users u 
                    ON is_uuid(ub.tailor) AND u.user_id = ub.tailor::uuid;
            """
            updated_tailor_name = await conn.fetchval(sql_update, tailor, bill_code)
            return updated_tailor_name  # Will be None if not updated
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
