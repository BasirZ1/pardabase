from typing import Optional

from helpers import make_supplier_dic
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
        bool: True if the supplier was added successfully, False otherwise.
    """

    try:
        async with connection_context() as conn:

            sql_insert = """
                INSERT INTO suppliers (name, phone, address, notes) 
                VALUES ($1, $2, $3, $4)
            """

            await conn.execute(sql_insert, name, phone, address, notes)
            return True

    except Exception as e:
        await flatbed('exception', f"in add_new_supplier_ps: {e}")
        return False


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
        bool: True if the update was successful, False otherwise.
    """
    try:
        async with connection_context() as conn:

            sql_update = f"""
                UPDATE suppliers
                SET name = $1, phone = $2, address = $3, notes = $4
                WHERE id = $5
            """

            await conn.execute(sql_update, name, phone, address, notes, idToEdit)
            return True

    except Exception as e:
        await flatbed('exception', f"In update_supplier: {e}")
        return False


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
        raise RuntimeError(f"Failed to get supplier: {e}")


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
        raise RuntimeError(f"Failed to get suppliers list: {e}")


async def remove_supplier_ps(supplier_id: int):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM suppliers WHERE id = $1", supplier_id)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_supplier_ps: {e}")
        return False
