#  Helper Functions
from datetime import datetime, date
from typing import Any, Iterable, Mapping, Callable, Optional, Dict, List, Union


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
                "createdAt": format_timestamp(data["created_at"]),
                "imageUrl": data["image_url"]
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


def get_formatted_products_for_sync_list(products_data):
    """
    Helper function to format products data into JSON-compatible objects.

    Parameters:
    - products_data: Raw data fetched from the database.

    Returns:
    - A list of formatted products dictionaries.
    """
    products_list = []
    if products_data:
        for data in products_data:
            product = make_product_dic_for_sync(data)
            products_list.append(product)
    return products_list


def get_formatted_rolls_for_sync_list(rolls_data):
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
            roll = make_roll_dic_for_sync(data)
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


def get_formatted_entities_list(entities_data):
    """
    Helper function to format entities data into JSON-compatible objects.

    Parameters:
    - entities_data: Raw data fetched from the database.

    Returns:
    - A list of formatted entities dictionaries.
    """
    entities_list = []
    if entities_data:
        for data in entities_data:
            entity = make_entity_dic(data)
            entities_list.append(entity)
    return entities_list


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


def get_formatted_purchase_items(purchase_items_data):
    """
    Helper function to format purchase_items data into JSON-compatible objects.

    Parameters:
    - purchase_items_data: Raw data fetched from the database.

    Returns:
    - A list of formatted purchase_items dictionaries.
    """
    purchase_items = []
    if purchase_items_data:
        for data in purchase_items_data:
            purchase_item = make_purchase_item_dic(data)
            purchase_items.append(purchase_item)
    return purchase_items


def get_formatted_users_small_list(users_data):
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
            user = make_user_dic(data)
            users_list.append(user)
    return users_list


def get_formatted_payments_list(payments_data):
    """
    Helper function to format payments data into JSON-compatible objects.

    Parameters:
    - payments_data: Raw data fetched from the database.

    Returns:
    - A list of formatted payments dictionaries.
    """
    payments_list = []
    if payments_data:
        for data in payments_data:
            payment = make_payment_dic(data)
            payments_list.append(payment)
    return payments_list


def get_formatted_misc_list(misc_records_data):
    """
    Helper function to format misc_records data into JSON-compatible objects.

    Parameters:
    - misc_records_data: Raw data fetched from the database.

    Returns:
    - A list of formatted misc dictionaries.
    """
    misc_list = []
    if misc_records_data:
        for data in misc_records_data:
            misc = make_misc_dic(data)
            misc_list.append(misc)
    return misc_list


def get_formatted_earnings_list(earnings_data):
    """
    Helper function to format earnings data into JSON-compatible objects.

    Parameters:
    - earnings_data: Raw data fetched from the database.

    Returns:
    - A list of formatted earning dictionaries.
    """
    earnings_list = []
    if earnings_data:
        for data in earnings_data:
            earning = make_earning_dic(data)
            earnings_list.append(earning)
    return earnings_list


def get_formatted_id_name_list(pg_data):
    """
    Helper function to format pg data into JSON-compatible objects.

    Parameters:
    - pg_data: Raw data fetched from the database.

    Returns:
    - A list of formatted (id, name) dictionaries.
    """
    _list = []
    if pg_data:
        for data in pg_data:
            dic = make_id_name_dic(data)
            _list.append(dic)
    return _list


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


# def parse_date(val: Any) -> Union[date, datetime, None]:
#     """
#     Parses a string to date or datetime object.
#     - If string has only date (YYYY-MM-DD) → returns date object.
#     - If string has date and time (YYYY-MM-DD HH:MM[:SS]) → returns datetime object.
#     - If already date/datetime → returns as is.
#     """
#     if isinstance(val, str):
#         try:
#             # Try parsing as datetime first
#             dt = datetime.fromisoformat(val)
#             return dt if dt.time() != datetime.min.time() else dt.date()
#         except ValueError:
#             pass  # Fall back to strict date parsing
#
#         try:
#             # Try parsing date format explicitly if isoformat fails
#             return datetime.strptime(val, "%Y-%m-%d").date()
#         except ValueError:
#             pass  # Invalid format, let it pass through
#
#     if isinstance(val, (date, datetime)):
#         return val
#
#     return None  # For None or unexpected types

# def parse_date(val: Any) -> Union[date, datetime, None]:
#     """
#     Reverse of format_date:
#     - "YYYY-MM-DD" -> date object
#     - "YYYY-MM-DD HH:MM:SS" -> datetime object (naive)
#     - Already a date/datetime -> returned as is
#     - Anything else -> None
#     """
#     if isinstance(val, str):
#         try:
#             # Match datetime with seconds
#             return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
#         except ValueError:
#             pass
#         try:
#             # Match pure date
#             return datetime.strptime(val, "%Y-%m-%d").date()
#         except ValueError:
#             pass
#
#     if isinstance(val, (date, datetime)):
#         return val
#
#     return None


def parse_date(val: Any) -> Optional[Union[date, datetime]]:
    """
    Parse input into date or datetime:
    - "YYYY-MM-DD" -> date
    - "YYYY-MM-DD[ T]HH:MM[:SS[.ffffff]][±HH:MM]" -> datetime
    - Already a date/datetime -> returned as is
    - Else -> None
    """
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val)
            # If the string was just YYYY-MM-DD, fromisoformat gives a datetime at midnight.
            # Detect that and return a pure date instead.
            if dt.time() == datetime.min.time() and "T" not in val and " " not in val:
                return dt.date()
            return dt
        except ValueError:
            return None

    if isinstance(val, datetime):
        return val

    if isinstance(val, date):
        return val

    return None


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
        "imageUrl": data["image_url"],
        "costPerMetre": data["cost_per_metre"]
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


def make_entity_dic(data):
    entity = {
        "id": data["id"],
        "name": data["name"],
        "phone": data["phone"],
        "address": data["address"],
        "notes": data["notes"]
    }
    return entity


def make_supplier_details_dic(data):
    supplier_details = {
        "purchasesTotalAFN": data["purchases_total_afn"],
        "purchasesTotalUSD": data["purchases_total_usd"],
        "purchasesTotalCNY": data["purchases_total_cny"],
        "payableTotalAFN": data["payable_total_afn"],
        "payableTotalUSD": data["payable_total_usd"],
        "payableTotalCNY": data["payable_total_cny"],
        "receivableTotalAFN": data["receivable_total_afn"],
        "receivableTotalUSD": data["receivable_total_usd"],
        "receivableTotalCNY": data["receivable_total_cny"],
        "totalPaidAFN": data["total_paid_afn"],
        "totalPaidUSD": data["total_paid_usd"],
        "totalPaidCNY": data["total_paid_cny"]
    }
    return supplier_details


def make_entity_details_dic(data):
    entity_details = {
        "payableTotalAFN": data["payable_total_afn"],
        "payableTotalUSD": data["payable_total_usd"],
        "payableTotalCNY": data["payable_total_cny"],
        "receivableTotalAFN": data["receivable_total_afn"],
        "receivableTotalUSD": data["receivable_total_usd"],
        "receivableTotalCNY": data["receivable_total_cny"]
    }
    return entity_details


def make_id_name_dic(data):
    dic = {
        "id": data["id"],
        "name": data["name"]
    }
    return dic


def make_purchase_dic(data):
    purchase = {
        "id": data["id"],
        "supplierId": data["supplier_id"],
        "supplierName": data["supplier_name"],
        "totalAmount": data["total_amount"],
        "currency": data["currency"],
        "description": data["description"],
        "createdAt": format_date(data["created_at"]),
        "updatedAt": format_date(data["updated_at"]),
        "createdBy": data["created_by"]
    }
    return purchase


def make_purchase_item_dic(data):
    purchase_item = {
        "id": data["id"],
        "purchaseId": data["purchase_id"],
        "categoryIndex": data["category_index"],
        "productCode": data["product_code"],
        "productName": data["product_name"],
        "costPerMetre": data["cost_per_metre"],
        "rollsList": []
    }
    return purchase_item


def make_employment_info_dic(data):
    employment_info = {
        "id": data["id"],
        "userId": data["user_id"],
        "salaryAmount": data["salary_amount"],
        "salaryStartDate": format_date(data["salary_start_date"]),
        "tailorType": data["tailor_type"],
        "salesmanStatus": data["salesman_status"],
        "billBonusPercent": data["bill_bonus_percent"],
        "note": data["note"],
        "salaryCycle": data["salary_cycle"],
        "isActive": data["is_active"]
    }
    return employment_info


def make_profile_data_dic(data):
    profile_data = {
        "totalEarnings": data["total_earnings"],
        "totalWithdrawals": data["total_withdrawals"]
    }
    return profile_data


def make_user_dic(data):
    user = {
        "userId": data["user_id"],
        "fullName": data["full_name"]
    }
    return user


def make_payment_dic(data):
    payment = {
        "id": data["id"],
        "amount": data["amount"],
        "currency": data["currency"],
        "note": data["note"],
        "payedByName": data["payed_by_name"],
        "createdAt": format_date(data["created_at"])
    }
    return payment


def make_misc_dic(data):
    misc = {
        "id": data["id"],
        "transactionType": data["transaction_type"],
        "amount": data["amount"],
        "currency": data["currency"],
        "direction": data["direction"],
        "note": data["note"],
        "createdBy": data["created_by"],
        "createdAt": format_date(data["created_at"])
    }
    return misc


def make_earning_dic(data):
    earning = {
        "id": data["id"],
        "amount": data["amount"],
        "earningType": data["earning_type"],
        "reference": data["reference"],
        "note": data["note"],
        "createdAt": format_date(data["created_at"]),
        "addedBy": data["added_by_display"]
    }
    return earning


def make_product_dic_for_sync(data):
    """Full product dictionary including all fields needed for offline sync."""
    return {
        "productCode": data["product_code"],
        "name": data["name"],
        "categoryIndex": data["category"],
        "quantityInCm": data["quantity"],
        "pricePerMetre": data["price_per_metre"],
        "description": data["description"],
        "imageUrl": data["image_url"],
        "archived": data["archived"],
        "createdAt": format_date(data["created_at"]),
        "updatedAt": format_date(data["updated_at"])
    }


def make_roll_dic_for_sync(data):
    """Full roll dictionary including all fields needed for offline sync."""
    return {
        "productCode": data["product_code"],
        "rollCode": data["roll_code"],
        "quantityInCm": data["quantity"],
        "colorLetter": data["color"],
        "imageUrl": data["image_url"],
        "costPerMetre": data["cost_per_metre"],
        "archived": data["archived"],
        "createdAt": format_date(data["created_at"]),
        "updatedAt": format_date(data["updated_at"])
    }
