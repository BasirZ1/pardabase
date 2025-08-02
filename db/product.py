from helpers import make_roll_dic, make_product_dic
from utils import flatbed
from utils.conn import connection_context


async def insert_new_product(name, category_index, cost_per_metre, price, description):
    try:
        async with connection_context() as conn:
            sql_insert = """
                INSERT INTO products (
                    name,
                    category,
                    cost_per_metre,
                    price_per_metre,
                    description
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING product_code
            """
            product_code = await conn.fetchval(sql_insert, name, category_index, cost_per_metre, price,
                                               description)

            return product_code
    except Exception as e:
        await flatbed('exception', f"In insert_new_product: {e}")
        return None


async def update_product(codeToEdit, name, category_index, cost_per_metre, price, description):
    try:
        async with connection_context() as conn:
            sql_update = """
                UPDATE products
                SET name = $1,
                category = $2, cost_per_metre = $3,
                price_per_metre = $4, description = $5,
                updated_at = now()
                WHERE product_code = $6
                RETURNING product_code
            """
            product_code = await conn.fetchval(sql_update, name, category_index, cost_per_metre,
                                               price, description, codeToEdit)

            return product_code
    except Exception as e:
        await flatbed('exception', f"in update_product: {e}")
        return None


async def search_products_list(search_query, search_by):
    """
    Retrieve products list based on a search query and filter with search_by.

    Parameters:
    - search_query (str): The term to search within the specified field.
    - search_by (int): The field to search in (0 for 'code', 1 for 'name'). Defaults to 'name' if not recognized.

    Returns:
    - List of records from the products table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_products_list($1, $2);"
            products_list = await conn.fetch(query, search_query, search_by)
            return products_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_products_list: {e}")
        raise RuntimeError(f"Failed to search products: {e}")


async def search_products_list_filtered(stock_condition, category):
    """
    Retrieve products list based on a date or category filter.

    Parameters:
    - date (int): The date filter for products list.
    - category (int): The index for the type of the category:

    Returns:
    - List of records from the products table that match the criteria.
    """
    try:
        async with connection_context() as conn:
            query = "SELECT * FROM search_products_list_filtered($1, $2);"
            expenses_list = await conn.fetch(query, stock_condition, category)
            return expenses_list  # Returns a list of asyncpg Record objects

    except Exception as e:
        await flatbed('exception', f"In search_products_list_filtered: {e}")
        raise RuntimeError(f"Failed to search products: {e}")


async def get_product_and_roll_ps(code):
    try:
        async with connection_context() as conn:
            upper_code = code.upper()
            if "R" in upper_code:
                product_code, roll_code = upper_code.split("R", 1)
                roll_code = f"R{roll_code}"
            else:
                product_code, roll_code = upper_code, None

            # Fetch the product
            query_product = "SELECT * FROM search_products_list($1, 0, 1, true);"
            product = await conn.fetchrow(query_product, product_code)

            if not product:
                return None

            # asyncpg returns a dictionary-like object, so we use column names directly
            product_dict = make_product_dic(product)

            # Fetch the specific roll
            if roll_code:
                query_roll = """
                SELECT 
                    r.product_code, 
                    r.roll_code, 
                    r.quantity, 
                    r.color, 
                    r.image_url,
                    pi.cost_per_metre
                FROM rolls r
                LEFT JOIN purchase_items pi ON r.purchase_item_id = pi.id
                WHERE r.product_code = $1 AND r.roll_code = $2 AND r.archived = false
                """
                roll = await conn.fetchrow(query_roll, product_code, roll_code)

                if roll:
                    roll_dict = make_roll_dic(roll)
                    product_dict["rollsList"].append(roll_dict)

            return product_dict

    except Exception as e:
        await flatbed('exception', f"In get_product_and_roll_ps: {e}")
        return None


async def get_roll_and_product_ps(code):
    try:
        async with connection_context() as conn:
            roll_code = code.upper()
            # Fetch the specific roll
            query_roll = """
            SELECT 
                r.product_code, 
                r.roll_code, 
                r.quantity, 
                r.color, 
                r.image_url,
                pi.cost_per_metre
            FROM rolls r
            LEFT JOIN purchase_items pi ON r.purchase_item_id = pi.id
            WHERE r.roll_code = $1 AND r.archived = false
            """
            roll = await conn.fetchrow(query_roll, roll_code)

            if not roll:
                return None

            roll_dict = make_roll_dic(roll)

            # Fetch the product
            query_product = "SELECT * FROM search_products_list($1, 0, 1, true);"
            product = await conn.fetchrow(query_product, roll_dict["productCode"])

            if not product:
                return None

            product_dict = make_product_dic(product)

            product_dict["rollsList"].append(roll_dict)

            return product_dict

    except Exception as e:
        await flatbed('exception', f"In get_roll_and_product_ps: {e}")
        return None


async def remove_product_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("DELETE FROM products WHERE product_code = $1", code)
        return True
    except Exception as e:
        await flatbed('exception', f"in remove_product_ps: {e}")
        return False


async def archive_product_ps(code):
    try:
        async with connection_context() as conn:
            await conn.execute("""
                UPDATE rolls
                SET archived = TRUE, updated_at = now()
                WHERE product_code = $1
            """, code)
            await conn.execute("""
                UPDATE products
                SET archived = TRUE, updated_at = now()
                WHERE product_code = $1
            """, code)
        return True
    except Exception as e:
        await flatbed('exception', f"in archive_product_ps: {e}")
        return False
