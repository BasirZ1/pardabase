#  Helper Functions
from datetime import datetime, date
from typing import Any, Iterable, Mapping, Callable, Optional, Dict, List


def get_formatted_recent_activities_list(recent_activity_data):
    """
    Helper function to format recent activities data into JSON-compatible objects.

    Parameters:
    - logs_data: Raw data fetched from the database.

    Returns:
    - A list of formatted recent activities dictionaries.
    """
    recent_activity_list = []
    if recent_activity_data:
        for data in recent_activity_data:
            activity = {
                "id": data["id"],
                "date": data["date"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(data["date"], datetime)
                else data["date"],
                "username": data["username"],
                "action": data["action"],
            }
            recent_activity_list.append(activity)
    return recent_activity_list


def get_formatted_tags_list(tags_data):
    """
    Helper function to format tags data into JSON-compatible objects.

    Parameters:
    - tags_data: Raw data fetched from the database.

    Returns:
    - A list of formatted tags dictionaries.
    """
    tags_list = []
    if tags_data:
        for data in tags_data:
            tag = {
                "fullCode": data["full_code"],
                "productName": data["product_name"],
                "categoryIndex": data["category"],
                "colorLetter": data["color"],
                "createdOn": data["created_on"].strftime('%Y-%m-%d')
                if isinstance(data["created_on"], (date, datetime)) else data["created_on"]
            }
            tags_list.append(tag)
    return tags_list


def get_formatted_expenses_list(expenses_data):
    """
    Helper function to format expenses data into JSON-compatible objects.

    Parameters:
    - expenses_data: Raw data fetched from the database.

    Returns:
    - A list of formatted expenses dictionaries.
    """
    expenses_list = []
    if expenses_data:
        for data in expenses_data:
            search_result = make_expense_dic(data)
            expenses_list.append(search_result)

    return expenses_list


def get_formatted_search_results_list(products_data, bills_data):
    """
    Helper function to format products data and bills_data into JSON-compatible objects.

    Parameters:
    - products_data: Raw data fetched from the database.
    - bills_data: Raw data fetched from the database.

    Returns:
    - A list of formatted search_results dictionaries.
    """
    search_results_list = []
    if products_data:
        for data in products_data:
            search_result = make_product_dic(data)
            search_results_list.append(search_result)

    if bills_data:
        for data in bills_data:
            search_result = make_bill_dic(data)
            search_results_list.append(search_result)

    return search_results_list


def get_formatted_rolls_list(rolls_data):
    """
    Helper function to format rolls data into JSON-compatible objects.

    Parameters:
    - rolls_data: Raw data fetched from the database.

    Returns:
    - A list of formatted rolls dictionaries.
    """
    rolls_list = []
    if rolls_data:
        for data in rolls_data:
            roll = make_roll_dic(data)
            rolls_list.append(roll)
    return rolls_list


def get_formatted_users_list(users_data):
    """
    Helper function to format users data into JSON-compatible objects.

    Parameters:
    - users_data: Raw data fetched from the database.

    Returns:
    - A list of formatted users dictionaries.
    """
    users_list = []
    if users_data:
        for data in users_data:
            user = {
                "userId": data["user_id"],
                "fullName": data["full_name"],
                "username": data["username"],
                "level": data["level"],
                "imageUrl": data["image_url"]
            }
            users_list.append(user)
    return users_list


def get_formatted_suppliers_list(suppliers_data):
    """
    Helper function to format suppliers data into JSON-compatible objects.

    Parameters:
    - suppliers_data: Raw data fetched from the database.

    Returns:
    - A list of formatted suppliers dictionaries.
    """
    suppliers_list = []
    if suppliers_data:
        for data in suppliers_data:
            supplier = make_supplier_dic(data)
            suppliers_list.append(supplier)
    return suppliers_list


def get_formatted_purchases_list(purchases_data):
    """
    Helper function to format purchases data into JSON-compatible objects.

    Parameters:
    - purchases_data: Raw data fetched from the database.

    Returns:
    - A list of formatted purchases dictionaries.
    """
    purchases_list = []
    if purchases_data:
        for data in purchases_data:
            purchase = make_purchase_dic(data)
            purchases_list.append(purchase)
    return purchases_list


def get_formatted_salesmen_list(salesmen_data):
    """
    Helper function to format salesmen data into JSON-compatible objects.

    Parameters:
    - salesmen_data: Raw data fetched from the database.

    Returns:
    - A list of formatted salesmen dictionaries.
    """
    salesmen_list = []
    if salesmen_data:
        for data in salesmen_data:
            salesman = make_salesman_dic(data)
            salesmen_list.append(salesman)
    return salesmen_list


def get_formatted_tailors_list(tailors_data):
    """
    Helper function to format tailors data into JSON-compatible objects.

    Parameters:
    - tailors_data: Raw data fetched from the database.

    Returns:
    - A list of formatted tailors dictionaries.
    """
    tailors_list = []
    if tailors_data:
        for data in tailors_data:
            tailor = make_tailor_dic(data)
            tailors_list.append(tailor)
    return tailors_list


def get_formatted_suppliers_small_list(suppliers_data):
    """
    Helper function to format suppliers data into JSON-compatible objects.

    Parameters:
    - suppliers_data: Raw data fetched from the database.

    Returns:
    - A list of formatted suppliers dictionaries.
    """
    suppliers_list = []
    if suppliers_data:
        for data in suppliers_data:
            supplier = make_supplier_small_dic(data)
            suppliers_list.append(supplier)
    return suppliers_list


# def _ts(val: Any) -> Any:
#     """Convert datetime → 'YYYY‑MM‑DD HH:MM:SS'; leave everything else unchanged."""
#     return val.strftime('%Y-%m-%d %H:%M:%S') if isinstance(val, datetime) else val
#
#
# def format_date(val):
#     return val.isoformat() if isinstance(val, (date, datetime)) else val


def format_timestamp(val: Any) -> Any:
    """Convert datetime → 'YYYY-MM-DD HH:MM:SS'; leave everything else unchanged.
    Handles both naive and timezone-aware datetimes (timestamptz)."""
    if isinstance(val, datetime):
        if val.tzinfo is not None:  # Timezone-aware datetime
            return val.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
        return val.strftime('%Y-%m-%d %H:%M:%S')
    return val


def format_date(val: Any) -> Any:
    """Convert date/datetime → ISO format string; leave everything else unchanged.
    Handles both naive and timezone-aware datetimes (timestamptz)."""
    if isinstance(val, datetime):
        if val.tzinfo is not None:  # Timezone-aware datetime
            return val.isoformat(timespec='seconds')  # Includes timezone info
        return val.isoformat(timespec='seconds')
    if isinstance(val, date):
        return val.isoformat()
    return val


def format_cut_fabric_records(
        rows: Iterable[Mapping[str, Any]],
        *,
        extra: Optional[Mapping[str, str]] = None,
        transformer: Optional[Callable[[Any], Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convert asyncpg Records (or dict‑like objects) to JSON‑ready dicts.

    Parameters
    ----------
    rows        : iterable of Records
    extra       : mapping {dest_key: src_field} for additional columns
    transformer : function applied to every value (defaults to _ts)

    Returns
    -------
    List of dicts
    """
    extra = extra or {}
    xf = transformer or format_timestamp  # choose the transformer only once

    formatted: List[Dict[str, Any]] = []
    append = formatted.append  # local ref for speed in large loops

    for r in rows or []:
        d = {
            "id": xf(r["id"]),
            "rollCode": xf(r["roll_code"]),
            "billCode": xf(r["bill_code"]),
            "createdBy": xf(r["created_by"]),
            "quantity": xf(r["quantity"]),
            "status": xf(r["status"]),
            "comment": xf(r["comment"]),
            "createdAt": xf(r["created_at"]),
        }
        for dest_key, src_field in extra.items():
            d[dest_key] = xf(r[src_field])
        append(d)

    return formatted


def make_bill_dic(data):
    bill = {
        "billCode": data["bill_code"],
        "billDate": format_date(data["bill_date"]),
        "dueDate": format_date(data["due_date"]),
        "customerName": data["customer_name"],
        "customerNumber": data["customer_number"],
        "price": data["price"],
        "paid": data["paid"],
        "remaining": data["remaining"],
        "fabrics": data["fabrics"],
        "parts": data["parts"],
        "status": data["status"],
        "salesman": data["salesman"],
        "salesmanName": data["salesman_name"],
        "tailor": data["tailor"],
        "tailorName": data["tailor_name"],
        "additionalData": data["additional_data"],
        "installation": data["installation"]
    }
    return bill


def make_expense_dic(data):
    expense = {
        "id": data["id"],
        "categoryIndex": data["category_index"],
        "description": data["description"],
        "amount": data["amount"],
        "date": data["date"].isoformat() if isinstance(data["date"],
                                                       (date, datetime)) else data["date"]
    }
    return expense


def make_product_dic(data):
    product = {
        "productCode": data["product_code"],
        "name": data["name"],
        "categoryIndex": data["category"],
        "quantityInCm": data["quantity"],
        "costPerMetre": data["cost_per_metre"],
        "pricePerMetre": data["price_per_metre"],
        "description": data["description"],
        "imageUrl": data["image_url"],
        "rollsList": []
    }
    return product


def make_roll_dic(data):
    roll = {
        "productCode": data["product_code"],
        "rollCode": data["roll_code"],
        "quantityInCm": data["quantity"],
        "colorLetter": data["color"],
        "imageUrl": data["image_url"]
    }
    return roll


def make_supplier_dic(data):
    supplier = {
        "id": data["id"],
        "name": data["name"],
        "phone": data["phone"],
        "address": data["address"],
        "notes": data["notes"]
    }
    return supplier


def make_supplier_small_dic(data):
    supplier = {
        "id": data["id"],
        "name": data["name"]
    }
    return supplier


def make_purchase_dic(data):
    purchase = {
        "id": data["id"],
        "supplierId": data["supplier_id"],
        "totalAmount": data["total_amount"],
        "currency": data["currency"],
        "description": data["description"],
        "createdAt": format_date(data["created_at"]),
        "updatedAt": format_date(data["updated_at"]),
        "createdBy": data["created_by"]
    }
    return purchase


def make_employment_info_dic(data):
    employment_info = {
        "id": data["id"],
        "userId": data["user_id"],
        "salaryAmount": data["salary_amount"],
        "salaryStartDate": format_date(data["salary_start_date"]),
        "tailorType": data["tailor_type"],
        "salesmanStatus": data["salesman_status"],
        "billBonusPercent": data["bill_bonus_percent"],
        "note": data["note"]
    }
    return employment_info


def make_salesman_dic(data):
    salesman = {
        "userId": data["user_id"],
        "fullName": data["full_name"]
    }
    return salesman


def make_tailor_dic(data):
    tailor = {
        "userId": data["user_id"],
        "fullName": data["full_name"]
    }
    return tailor
