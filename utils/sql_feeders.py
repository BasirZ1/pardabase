from utils.conn import get_connection


def insert_into_inventory(code, image, name, category_index, quantity, price, description):
    """
    Adds a new item to the inventory.

    Args:
        code (str): The unique code for the inventory item.
        image (bytes): The binary data of the item's image.
        name (str): The name of the inventory item.
        category_index (int): The index of the category for the inventory item.
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
                INSERT INTO inventory (
                    code,
                    image,
                    name,
                    category,
                    quantity_in_cm,
                    price_per_metre,
                    description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                code,
                image,
                name,
                category_index,
                quantity,
                price,
                description
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error adding item to inventory: {e}")
        return False
    finally:
        conn.close()


def update_in_inventory(code, new_code, image, name, category_index, quantity, price, description):
    """
    Update an item in the inventory.

    Args:
        code (str): The unique code for the inventory item.
        new_code (str): The unique code for the inventory item.
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
                SET code = %s, image = %s, name = %s,
                category = %s, quantity_in_cm = %s,
                price_per_metre = %s, description = %s
                WHERE code = %s
            """
            values = (
                new_code,
                image,
                name,
                category_index,
                quantity,
                price,
                description,
                code
            )

            cur.execute(sql_insert, values)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error updating item in inventory: {e}")
        return False
    finally:
        conn.close()
