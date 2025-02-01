import re
from typing import Optional

from .logger import flatbed
from utils.conn import get_connection


def insert_into_inventory(image, name, category_index, cost_per_metre, price, description):
    """
    Adds a new item to the inventory with an auto-generated product code.

    Args:
        image (bytes): The binary data of the item's image.
        name (str): The name of the inventory item.
        category_index (int): The index of the category for the inventory item.
        cost_per_metre (int): The cost of the item per metre.
        price (int): The price of the item per metre.
        description (str): A description of the inventory item.

    Returns:
        str: The product code if the item was added successfully, None otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Generate the new product code
            cur.execute("SELECT MAX(code) FROM inventory WHERE code LIKE 'P%'")
            last_code = cur.fetchone()[0]

            if last_code:
                # Extract only the first numeric part from the code
                match = re.search(r'P(\d+)', last_code)  # Matches 'P' followed by digits
                if match:
                    last_number = int(match.group(1))  # Extract the first number group
                    new_number = last_number + 1
                else:
                    new_number = 1  # Start with 1 if no valid number is found
            else:
                new_number = 1  # Start with 1 if no codes exist

            product_code = f"P{new_number}"  # Generate the new product code

            # SQL query to insert the item into the inventory table
            sql_insert = """
                INSERT INTO inventory (
                    code,
                    image,
                    name,
                    category,
                    cost_per_metre,
                    price_per_metre,
                    description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                product_code,  # Insert the generated product code
                image,
                name,
                category_index,
                cost_per_metre,
                price,
                description
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return product_code  # Return the product code upon success
    except Exception as e:
        flatbed('exception', f"In insert_into_inventory: {e}")
        return None
    finally:
        conn.close()


def update_in_inventory(codeToEdit, image, name, category_index, cost_per_metre, price, description):
    """
    Update an item in the inventory.

    Args:
        codeToEdit (str): The unique code for the inventory item.
        image (bytes): The binary data of the item's image.
        name (str): The name of the inventory item.
        category_index (int): The category of the inventory item.
        cost_per_metre (int): The quantity of the item in centimeters.
        price (int): The price of the item per meter.
        description (str): A description of the inventory item.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # SQL query to insert the item into the inventory table
            sql_insert = """
                UPDATE inventory
                SET image = %s, name = %s,
                category = %s, cost_per_metre = %s,
                price_per_metre = %s, description = %s
                WHERE code = %s
            """
            values = (
                image,
                name,
                category_index,
                cost_per_metre,
                price,
                description,
                codeToEdit
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return True
    except Exception as e:
        flatbed('exception', f"Error updating item in inventory: {e}")
        return False
    finally:
        conn.close()


def update_roll_quantity_ps(roll_code, quantity, action):
    """
    Update a roll's quantity in the rolls table.

    Args:
        roll_code (str): The unique code for the roll.
        quantity (int): The quantity of the item in centimeters.
        action (str): The operation to be performed (subtract, add).

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    if action not in ["subtract", "add"]:
        flatbed('error', f"Invalid action: {action}. Expected 'subtract' or 'add'.")
        return False

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Determine the SQL operation
            sign = "-" if action == "subtract" else "+"

            # SQL query to update the product quantity
            sql_update = f"""
                UPDATE rolls
                SET quantity = quantity {sign} %s
                WHERE roll_code = %s
            """
            cur.execute(sql_update, (quantity, roll_code))
            conn.commit()

        return True
    except Exception as e:
        flatbed('exception', f"In update_roll_quantity_ps: {e}")
        return False
    finally:
        conn.close()


def add_expense_ps(category_index, description, amount):
    """
    Add an expense in the expenses table.

    Args:
        category_index (int): The category index for the expense.
        description (str): The description of the expense.
        amount (int): The amount of the expense.

    Returns:
        str: Return id if it was added successfully, None otherwise.
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # SQL query to add the expense
            sql_insert = """
            INSERT INTO expenses (category_index, description, amount)
            VALUES (%s, %s, %s)
            RETURNING id;
            """
            cur.execute(sql_insert, (category_index, description, amount))
            expense_id = cur.fetchone()[0]  # Retrieve the returned id
            conn.commit()

        return expense_id
    except Exception as e:
        flatbed('exception', f"In add_expense_ps: {e}")
        return None
    finally:
        conn.close()


def insert_into_rolls(product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    """
        Adds a new roll to the rolls with an auto-generated roll code.

        Args:
            image_data (bytes): The binary data of the item's image.
            product_code (str): The name of the inventory item.
            quantity (int): The quantity of the roll in cm.
            color_letter (str): The letter for color.

        Returns:
            str: The roll+product code if the item was added successfully, None otherwise.
        """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Generate the new product code
            cur.execute("SELECT MAX(roll_code) FROM rolls WHERE roll_code LIKE 'R%'")
            last_code = cur.fetchone()[0]

            if last_code:
                # Extract only the first numeric part from the code
                match = re.search(r'R(\d+)', last_code)  # Matches 'R' followed by digits
                if match:
                    last_number = int(match.group(1))  # Extract the first number group
                    new_number = last_number + 1
                else:
                    new_number = 1  # Start with 1 if no valid number is found
            else:
                new_number = 1  # Start with 1 if no codes exist

            roll_code = f"R{new_number}"  # Generate the new roll code

            # SQL query to insert the item into the rolls table
            sql_insert = """
                    INSERT INTO rolls (
                        product_code,
                        roll_code,
                        quantity,
                        color,
                        sample_image
                    ) VALUES (%s, %s, %s, %s, %s)
                """
            values = (
                product_code,
                roll_code,  # Insert the generated roll code
                quantity,
                color_letter,
                image_data
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return f"{product_code}{roll_code}"  # Return the product code upon success
    except Exception as e:
        flatbed('exception', f"In insert_into_rolls: {e}")
        return None
    finally:
        conn.close()


def update_in_rolls(codeToEdit, product_code, quantity, color_letter, image_data: Optional[bytes] = None):
    """
    Update a roll in the rolls table.

    Args:
        codeToEdit (str): The unique code for the roll.
        image_data (bytes): The binary data of the item's image.
        product_code (str): The name of the inventory item.
        quantity (int): The quantity of the roll in cm.
        color_letter (str): The letter for color.

    Returns:
        bool: True if the item was updated successfully, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # SQL query to insert the item into the inventory table
            sql_insert = """
                UPDATE rolls
                SET quantity = %s,
                color = %s, sample_image = %s
                WHERE roll_code = %s
            """
            values = (
                quantity,
                color_letter,
                image_data,
                codeToEdit
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return f"{product_code}{codeToEdit}"
    except Exception as e:
        flatbed('exception', f"Error updating roll in rolls: {e}")
        return None
    finally:
        conn.close()
