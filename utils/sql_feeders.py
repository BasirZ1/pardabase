import re

from .logger import flatbed
from utils.conn import get_connection


def insert_into_inventory(image, name, category_index, quantity, price, description, color_letter):
    """
    Adds a new item to the inventory with an auto-generated product code.

    Args:
        image (bytes): The binary data of the item's image.
        name (str): The name of the inventory item.
        category_index (int): The index of the category for the inventory item.
        quantity (int): The quantity of the item in centimeters.
        price (int): The price of the item per meter.
        description (str): A description of the inventory item.
        color_letter (str): A letter that determine the color of the item.

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
                
            category_letter = get_category_letter(category_index)
            product_code = f"P{new_number}{category_letter}{color_letter}"  # Generate the new product code

            # SQL query to insert the item into the inventory table
            sql_insert = """
                INSERT INTO inventory (
                    code,
                    image,
                    name,
                    category,
                    quantity_in_cm,
                    price_per_metre,
                    description,
                    color
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                product_code,  # Insert the generated product code
                image,
                name,
                category_index,
                quantity,
                price,
                description,
                color_letter
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return product_code  # Return the product code upon success
    except Exception as e:
        flatbed('exception', f"In insert_into_inventory: {e}")
        return None
    finally:
        conn.close()


def update_in_inventory(codeToEdit, image, name, category_index, quantity, price, description):
    """
    Update an item in the inventory.

    Args:
        codeToEdit (str): The unique code for the inventory item.
        image (bytes): The binary data of the item's image.
        name (str): The name of the inventory item.
        category_index (int): The category of the inventory item.
        quantity (int): The quantity of the item in centimeters.
        price (int): The price of the item per meter.
        description (str): A description of the inventory item.

    Returns:
        bool: True if the item was added successfully, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # SQL query to insert the item into the inventory table
            sql_insert = """
                UPDATE inventory
                SET image = %s, name = %s,
                category = %s, quantity_in_cm = %s,
                price_per_metre = %s, description = %s
                WHERE code = %s
            """
            values = (
                image,
                name,
                category_index,
                quantity,
                price,
                description,
                codeToEdit
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error updating item in inventory: {e}")
        return False
    finally:
        conn.close()


def get_category_letter(category_index):
    """
    Returns the category letter based on the category index.

    Args:
        category_index (int): The index of the category.

    Returns:
        str: The corresponding category letter, or None if the index is invalid.
    """
    if category_index == 0:
        return "P"
    elif category_index == 1:
        return "J"
    elif category_index == 2:
        return "D"
    elif category_index == 3:
        return "JP"
    elif category_index == 4:
        return "G"
    else:
        return None
