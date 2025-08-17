import re

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db import search_bills_list, get_product_and_roll_ps, get_roll_and_product_ps, search_products_list
from helpers import get_formatted_search_results_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.get("/search-results-list-get")
async def get_search_results_list(
        searchQuery: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Smart search for products and bills based on different query formats.
    """
    search_results_list = []

    bill_code_pattern = re.fullmatch(r"(?i)b\d+", searchQuery)  # `(?i)` makes it case insensitive
    product_code_pattern = re.fullmatch(r"(?i)p\d+", searchQuery)
    roll_code_pattern = re.fullmatch(r"(?i)p\d+r\d+", searchQuery)
    short_roll_code_pattern = re.fullmatch(r"(?i)r\d+", searchQuery)
    phone_number_pattern = re.fullmatch(r"\+?\d{4,14}", searchQuery)  # Intl. and local formats

    if bill_code_pattern:
        # Search bill by code
        bills_data = await search_bills_list(searchQuery, 0)
        search_results_list = get_formatted_search_results_list(None, bills_data)

    elif roll_code_pattern:
        product_data = await get_product_and_roll_ps(searchQuery)
        if product_data:
            search_results_list.append(product_data)

    elif short_roll_code_pattern:
        # Roll code like R2; get roll and product.
        product_data = await get_roll_and_product_ps(searchQuery)
        if product_data:
            search_results_list.append(product_data)

    elif product_code_pattern:
        # Search product by code
        products_data = await search_products_list(searchQuery, 0)
        search_results_list = get_formatted_search_results_list(products_data, None)

    elif phone_number_pattern:
        # Search bill by customer phone number
        bills_data = await search_bills_list(searchQuery, 2)
        search_results_list = get_formatted_search_results_list(None, bills_data)

    else:
        # General search (search both products and bills by name)
        products_data = await search_products_list(searchQuery, 1)
        bills_data = await search_bills_list(searchQuery, 1)
        search_results_list = get_formatted_search_results_list(products_data, bills_data)

    return JSONResponse(content=search_results_list, status_code=200)
