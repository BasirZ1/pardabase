from typing import Optional

from helpers import make_supplier_dic, make_supplier_details_dic
from utils import flatbed
from utils.conn import connection_context


async def insert_new_supplier(
        name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
):
    """
    Adds a new supplier to the database.

    Args:
        name (str): The name of the supplier.
        phone (Optional[str]): The phone number of the supplier.
        address (Optional[str]): The address of the supplier.
        notes (Optional[str]): Notes and data about the supplier.

    Returns:
        supplier_id: If the supplier was added successfully, return supplier_id else none.
    """

    try:
        async with connection_context() as conn:

            sql_insert = """
                INSERT INTO suppliers (name, phone, address, notes) 
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """

            supplier_id = await conn.fetchval(sql_insert, name, phone, address, notes)
            return supplier_id

    except Exception as e:
        await flatbed('exception', f"in add_new_supplier_ps: {e}")
        return None


async def update_supplier(
        idToEdit: int,
        name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
):
    """
    Updates supplier details in the database.

    Args:
        idToEdit (str): The id of the supplier to be updated.
        name (str): The new name of the supplier.
        phone (Optional[str]): The phone number of the supplier.
        address (Optional[str]): The address of the supplier.
        notes (Optional[str]): Notes and data about the supplier.

    Returns:
        supplier_id: If the update was successful, return supplier_id else None.
    """
    try:
        async with connection_context() as conn:

            sql_update = f"""
                UPDATE suppliers
                SET name = $1, phone = $2, address = $3, notes = $4
                WHERE id = $5
                RETURNING id
            """

            supplier_id = await conn.fetchval(sql_update, name, phone, address, notes, idToEdit)
            return supplier_id

    except Exception as e:
        await flatbed('exception', f"In update_supplier: {e}")
        return None


async def get_supplier_ps(supplier_id: int):
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow("""
                               SELECT * FROM suppliers
                               WHERE id = $1
                           """, supplier_id)
            if data:
                supplier = make_supplier_dic(data)
                return supplier

            return None
    except Exception as e:
        await flatbed('exception', f"In get_supplier_ps: {e}")
        raise


async def get_suppliers_list_ps():
    """
    Retrieve all suppliers from suppliers table.

    Returns:
    - All suppliers from the suppliers table.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM suppliers;"
            suppliers_list = await conn.fetch(query)
            return suppliers_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In get_suppliers_list_ps: {e}")
        raise


async def get_supplier_details_ps(supplier_id: int):
    """
     Retrieve a supplier's details like aggregated totals for purchases, payments,
     and miscellaneous transactions per currency.
     """
    try:
        async with connection_context() as conn:
            data = await conn.fetchrow("""
                WITH purchase_totals AS (
                    SELECT
                        SUM(CASE WHEN currency = 'AFN' THEN total_amount ELSE 0 END) AS purchases_total_afn,
                        SUM(CASE WHEN currency = 'USD' THEN total_amount ELSE 0 END) AS purchases_total_usd,
                        SUM(CASE WHEN currency = 'CNY' THEN total_amount ELSE 0 END) AS purchases_total_cny
                    FROM purchases
                    WHERE archived = FALSE AND supplier_id = $1
                ),
                payment_totals AS (
                    SELECT
                        SUM(CASE WHEN currency = 'AFN' THEN amount ELSE 0 END) AS total_paid_afn,
                        SUM(CASE WHEN currency = 'USD' THEN amount ELSE 0 END) AS total_paid_usd,
                        SUM(CASE WHEN currency = 'CNY' THEN amount ELSE 0 END) AS total_paid_cny
                    FROM supplier_payments
                    WHERE supplier_id = $1
                ),
                misc_totals AS (
                    SELECT
                        -- Payables (what you owe the supplier)
                        SUM(CASE WHEN direction = 'in'  AND currency = 'AFN' THEN amount ELSE 0 END) AS misc_payable_afn,
                        SUM(CASE WHEN direction = 'in'  AND currency = 'USD' THEN amount ELSE 0 END) AS misc_payable_usd,
                        SUM(CASE WHEN direction = 'in'  AND currency = 'CNY' THEN amount ELSE 0 END) AS misc_payable_cny,
                
                        -- Receivables (what supplier owes you)
                        SUM(CASE WHEN direction = 'out' AND currency = 'AFN' THEN amount ELSE 0 END) AS misc_receivable_afn,
                        SUM(CASE WHEN direction = 'out' AND currency = 'USD' THEN amount ELSE 0 END) AS misc_receivable_usd,
                        SUM(CASE WHEN direction = 'out' AND currency = 'CNY' THEN amount ELSE 0 END) AS misc_receivable_cny
                    FROM misc_transactions
                    WHERE supplier_id = $1
                )
                SELECT
                    COALESCE(pt.purchases_total_afn, 0) AS purchases_total_afn,
                    COALESCE(pt.purchases_total_usd, 0) AS purchases_total_usd,
                    COALESCE(pt.purchases_total_cny, 0) AS purchases_total_cny,
                    COALESCE(pay.total_paid_afn, 0) AS total_paid_afn,
                    COALESCE(pay.total_paid_usd, 0) AS total_paid_usd,
                    COALESCE(pay.total_paid_cny, 0) AS total_paid_cny,
                    
                    -- Misc transactions split
                    COALESCE(mt.misc_payable_afn, 0)    AS payable_total_afn,
                    COALESCE(mt.misc_payable_usd, 0)    AS payable_total_usd,
                    COALESCE(mt.misc_payable_cny, 0)    AS payable_total_cny,
                    COALESCE(mt.misc_receivable_afn, 0) AS receivable_total_afn,
                    COALESCE(mt.misc_receivable_usd, 0) AS receivable_total_usd,
                    COALESCE(mt.misc_receivable_cny, 0) AS receivable_total_cny
                    
                FROM purchase_totals pt, payment_totals pay, misc_totals mt
            """, supplier_id)

            if data:
                supplier_details = make_supplier_details_dic(data)
                return supplier_details

            return None
    except Exception as e:
        await flatbed('exception', f"In get_supplier_details_ps: {e}")
        raise


async def remove_supplier_ps(supplier_id: int):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM suppliers WHERE id = $1", supplier_id)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_supplier_ps: {e}")
        return False
