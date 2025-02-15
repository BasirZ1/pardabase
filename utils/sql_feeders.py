import json
from typing import Optional

from .logger import flatbed
from utils.conn import get_connection, release_connection


# def insert_new_product(image, name, category_index, cost_per_metre, price, description):
#     """
#     Adds a new product in the products table with an auto-generated product code.
#
#     Args:
#         image (bytes): The binary data of the product's image.
#         name (str): The name of the product.
#         category_index (int): The index of the category for the product.
#         cost_per_metre (int): The cost of the product per metre.
#         price (int): The price of the product per metre.
#         description (str): A description of the product.
#
#     Returns:
#         str: The product code if the item was added successfully, None otherwise.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#
#             # SQL query to insert the item into the inventory table
#             sql_insert = """
#                 INSERT INTO products (
#                     image,
#                     name,
#                     category,
#                     cost_per_metre,
#                     price_per_metre,
#                     description
#                 ) VALUES (%s, %s, %s, %s, %s, %s)
#                 RETURNING product_code
#             """
#             values = (
#                 image,
#                 name,
#                 category_index,
#                 cost_per_metre,
#                 price,
#                 description
#             )
#
#             cur.execute(sql_insert, values)
#             product_code = cur.fetchone()[0]
#             conn.commit()
#         return product_code  # Return the product code upon success
#     except Exception as e:
#         flatbed('exception', f"In insert_new_product: {e}")
#         return None
#     finally:
#         release_connection(conn)


async def insert_new_product(image, name, category_index, cost_per_metre, price, description):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO products (
                image,
                name,
                category,
                cost_per_metre,
                price_per_metre,
                description
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING product_code
        """
        product_code = await conn.fetchval(sql_insert, image, name, category_index, cost_per_metre, price, description)
        return product_code
    except Exception as e:
        flatbed('exception', f"In insert_new_product: {e}")
        return None
    finally:
        await release_connection(conn)


# def update_product(codeToEdit, image, name, category_index, cost_per_metre, price, description):
#     """
#     Update a product in the products table.
#
#     Args:
#         codeToEdit (str): The unique code for product.
#         image (bytes): The binary data of the product's image.
#         name (str): The name of the product.
#         category_index (int): The category of the product.
#         cost_per_metre (int): The quantity of the product in centimeters.
#         price (int): The price of the product per meter.
#         description (str): A description of the product.
#
#     Returns:
#         bool: True if the item was updated successfully, False otherwise.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             # SQL query to insert the item into the products table
#             sql_insert = """
#                 UPDATE products
#                 SET image = %s, name = %s,
#                 category = %s, cost_per_metre = %s,
#                 price_per_metre = %s, description = %s
#                 WHERE product_code = %s
#             """
#             values = (
#                 image,
#                 name,
#                 category_index,
#                 cost_per_metre,
#                 price,
#                 description,
#                 codeToEdit
#             )
#
#             cur.execute(sql_insert, values)
#             conn.commit()
#         return True
#     except Exception as e:
#         flatbed('exception', f"in update_product: {e}")
#         return False
#     finally:
#         release_connection(conn)


async def update_product(codeToEdit, image, name, category_index, cost_per_metre, price, description):
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE products
            SET image = $1, name = $2,
            category = $3, cost_per_metre = $4,
            price_per_metre = $5, description = $6
            WHERE product_code = $7
            RETURNING product_code
        """
        product_code = await conn.fetchval(sql_update, image, name,
                                           category_index, cost_per_metre, price, description, codeToEdit)

        return product_code is not None
    except Exception as e:
        flatbed('exception', f"in update_product: {e}")
        return False
    finally:
        await release_connection(conn)


# def update_roll_quantity_ps(roll_code, quantity, action):
#     """
#     Update a roll's quantity in the rolls table.
#
#     Args:
#         roll_code (str): The unique code for the roll.
#         quantity (int): The quantity of the item in centimeters.
#         action (str): The operation to be performed (subtract, add).
#
#     Returns:
#         bool: True if the item was updated successfully, False otherwise.
#     """
#     if action not in ["subtract", "add"]:
#         flatbed('error', f"Invalid action: {action}. Expected 'subtract' or 'add'.")
#         return False
#
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             # Determine the SQL operation
#             sign = "-" if action == "subtract" else "+"
#
#             # SQL query to update the product quantity
#             sql_update = f"""
#                 UPDATE rolls
#                 SET quantity = quantity {sign} %s
#                 WHERE roll_code = %s
#             """
#             cur.execute(sql_update, (quantity, roll_code))
#             conn.commit()
#
#         return True
#     except Exception as e:
#         flatbed('exception', f"In update_roll_quantity_ps: {e}")
#         return False
#     finally:
#         release_connection(conn)


async def update_roll_quantity_ps(roll_code, quantity, action):
    if action not in ["subtract", "add"]:
        flatbed('error', f"Invalid action: {action}. Expected 'subtract' or 'add'.")
        return False

    conn = await get_connection()
    try:
        sql_update = """
                    UPDATE rolls
                    SET quantity = quantity + 
                        CASE WHEN $1 = 'subtract' THEN -$2 ELSE $2 END
                    WHERE roll_code = $3
                    RETURNING quantity
                """
        updated_quantity = await conn.fetchval(sql_update, action, quantity, roll_code)

        return updated_quantity is not None

    except Exception as e:
        flatbed('exception', f"In update_roll_quantity_ps: {e}")
        return False
    finally:
        await release_connection(conn)


# def add_expense_ps(category_index, description, amount):
#     """
#     Add an expense in the expenses table.
#
#     Args:
#         category_index (int): The category index for the expense.
#         description (str): The description of the expense.
#         amount (int): The amount of the expense.
#
#     Returns:
#         str: Return id if it was added successfully, None otherwise.
#     """
#
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             # SQL query to add the expense
#             sql_insert = """
#             INSERT INTO expenses (category_index, description, amount)
#             VALUES (%s, %s, %s)
#             RETURNING id;
#             """
#             cur.execute(sql_insert, (category_index, description, amount))
#             expense_id = cur.fetchone()[0]  # Retrieve the returned id
#             conn.commit()
#
#         return expense_id
#     except Exception as e:
#         flatbed('exception', f"In add_expense_ps: {e}")
#         return None
#     finally:
#         release_connection(conn)


async def add_expense_ps(category_index, description, amount):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO expenses (category_index, description, amount)
            VALUES ($1, $2, $3)
            RETURNING id;
        """
        expense_id = await conn.fetchval(sql_insert, category_index, description, amount)

        return expense_id
    except Exception as e:
        flatbed('exception', f"In add_expense: {e}")
        return None
    finally:
        await release_connection(conn)


#
# def insert_new_roll(product_code, quantity, color_letter, image_data: Optional[bytes] = None):
#     """
#         Adds a new roll to the rolls with an auto-generated roll code.
#
#         Args:
#             image_data (bytes): The binary data of the roll's sample image.
#             product_code (str): The name of the product.
#             quantity (int): The quantity of the roll in cm.
#             color_letter (str): The letter for color.
#
#         Returns:
#             str: The product+roll code if the item was added successfully, None otherwise.
#         """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#
#             # SQL query to insert the roll into the rolls table
#             sql_insert = """
#                     INSERT INTO rolls (
#                         product_code,
#                         quantity,
#                         color,
#                         sample_image
#                     ) VALUES (%s, %s, %s, %s)
#                     returning roll_code
#                 """
#             values = (
#                 product_code,
#                 quantity,
#                 color_letter,
#                 image_data
#             )
#
#             cur.execute(sql_insert, values)
#             roll_code = cur.fetchone()[0]
#             conn.commit()
#         return f"{product_code}{roll_code}"  # Return the product code + roll code upon success
#     except Exception as e:
#         flatbed('exception', f"In insert_new_roll: {e}")
#         return None
#     finally:
#         release_connection(conn)


async def insert_new_roll(product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    conn = await get_connection()
    try:
        sql_insert = """
            INSERT INTO rolls (
                product_code,
                quantity,
                color,
                sample_image
            ) VALUES ($1, $2, $3, $4)
            RETURNING roll_code
        """
        roll_code = await conn.fetchval(sql_insert, product_code, quantity, color_letter, image_data)

        return f"{product_code}{roll_code}" if roll_code else None
    except Exception as e:
        flatbed('exception', f"In insert_new_roll: {e}")
        return None
    finally:
        await release_connection(conn)


# def update_roll(codeToEdit, product_code, quantity, color_letter, image_data: Optional[bytes] = None):
#     """
#     Update a roll in the rolls table.
#
#     Args:
#         codeToEdit (str): The unique code for the roll.
#         image_data (bytes): The binary data of the roll's sample image.
#         product_code (str): The name of the product.
#         quantity (int): The quantity of the roll in cm.
#         color_letter (str): The letter for color.
#
#     Returns:
#         bool: True if the item was updated successfully, False otherwise.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             # SQL query to update a roll in rolls table
#             sql_insert = """
#                 UPDATE rolls
#                 SET quantity = %s,
#                 color = %s, sample_image = %s
#                 WHERE roll_code = %s
#             """
#             values = (
#                 quantity,
#                 color_letter,
#                 image_data,
#                 codeToEdit
#             )
#
#             cur.execute(sql_insert, values)
#             conn.commit()
#         return f"{product_code}{codeToEdit}"
#     except Exception as e:
#         flatbed('exception', f"in update_roll: {e}")
#         return None
#     finally:
#         release_connection(conn)


async def update_roll(codeToEdit, product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE rolls
            SET quantity = $1,
                color = $2,
                sample_image = $3
            WHERE roll_code = $4
        """
        await conn.execute(sql_update, quantity, color_letter, image_data, codeToEdit)

        return f"{product_code}{codeToEdit}"
    except Exception as e:
        flatbed('exception', f"In update_roll: {e}")
        return None
    finally:
        await release_connection(conn)


# def insert_new_bill(
#     bill_date: Optional[str] = None,
#     due_date: Optional[str] = None,
#     customer_name: Optional[str] = None,
#     customer_number: Optional[str] = None,
#     price: Optional[int] = None,
#     paid: Optional[int] = None,
#     remaining: Optional[int] = None,
#     fabrics: Optional[str] = None,
#     parts: Optional[str] = None,
#     status: Optional[str] = 'pending',
#     salesman: Optional[str] = None,
#     tailor: Optional[str] = None,
#     additional_data: Optional[str] = None,
#     installation: Optional[str] = None
# ) -> Optional[str]:
#     """
#     Inserts a new bill into the bills table with an auto-generated bill code.
#
#     Args:
#         bill_date: The bill's date.
#         due_date: The bill's due date.
#         customer_name: The customer's name.
#         customer_number: The customer's contact number.
#         price: Total price.
#         paid: Amount paid.
#         remaining: Amount remaining.
#         fabrics: JSON string for fabrics.
#         parts: JSON string for parts.
#         status: Bill status (default 'pending').
#         salesman: Salesman responsible.
#         tailor: Tailor assigned.
#         additional_data: Extra JSON string.
#         installation: Installation details.
#
#     Returns:
#         The generated bill code if successful, or None on error.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#
#             sql_insert = """
#                 INSERT INTO bills (
#                     bill_date,
#                     due_date,
#                     customer_name,
#                     customer_number,
#                     price,
#                     paid,
#                     remaining,
#                     fabrics,
#                     parts,
#                     status,
#                     salesman,
#                     tailor,
#                     additional_data,
#                     installation
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s::jsonb, %s)
#                 returning bill_code
#             """
#             values = (
#                 bill_date,
#                 due_date,
#                 customer_name,
#                 customer_number,
#                 price,
#                 paid,
#                 remaining,
#                 fabrics,
#                 parts,
#                 status,
#                 salesman,
#                 tailor,
#                 additional_data,
#                 installation
#             )
#             cur.execute(sql_insert, values)
#             bill_code = cur.fetchone()[0]
#             conn.commit()
#         return bill_code
#     except Exception as e:
#         flatbed('exception', f"In insert_new_bill: {e}")
#         return None
#     finally:
#         release_connection(conn)


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
        status: Optional[str] = 'pending',
        salesman: Optional[str] = None,
        tailor: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    conn = await get_connection()
    try:
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
            status,
            salesman,
            tailor,
            additional_data,
            installation
        )
        return bill_code
    except Exception as e:
        flatbed('exception', f"In insert_new_bill: {e}")
        return None
    finally:
        await release_connection(conn)


# def update_bill(
#     bill_code: str,
#     bill_date: Optional[str] = None,
#     due_date: Optional[str] = None,
#     customer_name: Optional[str] = None,
#     customer_number: Optional[str] = None,
#     price: Optional[int] = None,
#     paid: Optional[int] = None,
#     remaining: Optional[int] = None,
#     fabrics: Optional[str] = None,
#     parts: Optional[str] = None,
#     status: Optional[str] = None,
#     salesman: Optional[str] = None,
#     tailor: Optional[str] = None,
#     additional_data: Optional[str] = None,
#     installation: Optional[str] = None
# ) -> Optional[str]:
#     """
#     Updates an existing bill in the bills table.
#
#     Args:
#         bill_code: The unique bill code.
#         bill_date: The bill's date.
#         due_date: The due date.
#         customer_name: The customer's name.
#         customer_number: The customer's contact number.
#         price: Total price.
#         paid: Amount paid.
#         remaining: Amount remaining.
#         fabrics: JSON string for fabrics.
#         parts: JSON string for parts.
#         status: Bill status.
#         salesman: Salesman responsible.
#         tailor: Tailor assigned.
#         additional_data: Extra JSON string.
#         installation: Installation details.
#
#     Returns:
#         The bill code if the update was successful, or None on error.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             sql_update = """
#                 UPDATE bills
#                 SET bill_date = %s,
#                     due_date = %s,
#                     customer_name = %s,
#                     customer_number = %s,
#                     price = %s,
#                     paid = %s,
#                     remaining = %s,
#                     fabrics = %s,
#                     parts = %s,
#                     status = %s,
#                     salesman = %s,
#                     tailor = %s,
#                     additional_data = %s,
#                     installation = %s,
#                     updated_at = NOW()
#                 WHERE bill_code = %s
#             """
#             values = (
#                 bill_date,
#                 due_date,
#                 customer_name,
#                 customer_number,
#                 price,
#                 paid,
#                 remaining,
#                 json.loads(fabrics) if fabrics else None,
#                 json.loads(parts) if parts else None,
#                 status,
#                 salesman,
#                 tailor,
#                 json.loads(additional_data) if additional_data else None,
#                 installation,
#                 bill_code
#             )
#             cur.execute(sql_update, values)
#             conn.commit()
#         return bill_code
#     except Exception as e:
#         flatbed('exception', f"in update_bill: {e}")
#         return None
#     finally:
#         release_connection(conn)


async def update_bill(
        bill_code: str,
        bill_date: Optional[str] = None,
        due_date: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_number: Optional[str] = None,
        price: Optional[int] = None,
        paid: Optional[int] = None,
        remaining: Optional[int] = None,
        fabrics: Optional[str] = None,
        parts: Optional[str] = None,
        status: Optional[str] = None,
        salesman: Optional[str] = None,
        tailor: Optional[str] = None,
        additional_data: Optional[str] = None,
        installation: Optional[str] = None
) -> Optional[str]:
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET bill_date = $1,
                due_date = $2,
                customer_name = $3,
                customer_number = $4,
                price = $5,
                paid = $6,
                remaining = $7,
                fabrics = $8::jsonb,
                parts = $9::jsonb,
                status = $10,
                salesman = $11,
                tailor = $12,
                additional_data = $13::jsonb,
                installation = $14,
                updated_at = NOW()
            WHERE bill_code = $15
        """
        await conn.execute(
            sql_update,
            bill_date,
            due_date,
            customer_name,
            customer_number,
            price,
            paid,
            remaining,
            json.loads(fabrics) if fabrics else None,
            json.loads(parts) if parts else None,
            status,
            salesman,
            tailor,
            json.loads(additional_data) if additional_data else None,
            installation,
            bill_code
        )
        return bill_code
    except Exception as e:
        flatbed('exception', f"In update_bill: {e}")
        return None
    finally:
        await release_connection(conn)


# def update_bill_status_ps(bill_code, status):
#     """
#     Update a bill's status in the bills table.
#
#     Args:
#         bill_code (str): The unique code for the bill.
#         status (str): The new status for the bill.
#
#     Returns:
#         bool: True if the item was updated successfully, False otherwise.
#     """
#
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             # SQL query to update the bill's status
#             sql_update = f"""
#                 UPDATE bills
#                 SET status = %s
#                 WHERE bill_code = %s
#             """
#             cur.execute(sql_update, (status, bill_code))
#             conn.commit()
#
#         return True
#     except Exception as e:
#         flatbed('exception', f"In update_bill_status_ps: {e}")
#         return False
#     finally:
#         release_connection(conn)
#


async def update_bill_status_ps(bill_code: str, status: str) -> bool:
    """
    Update a bill's status in the bills table.

    Args:
        bill_code (str): The unique code for the bill.
        status (str): The new status for the bill.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = await get_connection()
    try:
        sql_update = """
            UPDATE bills
            SET status = $1
            WHERE bill_code = $2
            RETURNING status
        """
        updated_status = await conn.fetchval(sql_update, status, bill_code)

        # asyncpg returns a string like 'UPDATE 1' if successful
        return updated_status is not None
    except Exception as e:
        flatbed('exception', f"In update_bill_status_ps: {e}")
        return False
    finally:
        await release_connection(conn)
