from utils.conn import get_connection


def insert_into_inventory(code, image, name, quantity, price, description):
    """
    Adds a new item to the inventory.

    Args:
        code (str): The unique code for the inventory item.
        image (bytes): The binary data of the item's image.
        name (str): The name of the inventory item.
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
                    quantity_in_cm,
                    price_per_metre,
                    description
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                code,
                image,
                name,
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


def update_product_image(code, image):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                UPDATE inventory
                SET image = %s
                WHERE code = %s
            """, (image, code))
    conn.commit()
    cur.close()
    conn.close()
