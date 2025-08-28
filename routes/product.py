import re
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse

from Models import RemoveRequest
from db import insert_new_product, handle_image_update, remember_users_action, update_product, \
    search_products_list_filtered, get_roll_and_product_ps, get_product_and_roll_ps, search_products_list, \
    remove_product_ps, archive_product_ps
from helpers import classify_image_upload, get_formatted_search_results_list
from utils import verify_jwt_user, flatbed

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-product")
async def add_or_edit_product(
        codeToEdit: Optional[str] = Form(None),
        name: str = Form(...),
        categoryIndex: int = Form(...),
        price: int = Form(...),
        description: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    image_status, image_data = await classify_image_upload(image)

    if codeToEdit is None:
        # CREATE NEW
        product_code = await insert_new_product(name, categoryIndex, price, description)
        if not product_code:
            return JSONResponse(content={"result": False, "code": product_code, "name": name})

        await handle_image_update("product", user_data['tenant'], product_code, image_status, image_data)
        await remember_users_action(user_data['user_id'], f"Product Added: {product_code}")
    else:
        # UPDATE EXISTING
        product_code = await update_product(codeToEdit, name, categoryIndex, price, description)
        if not product_code:
            return JSONResponse(content={"result": False, "code": product_code, "name": name})

        await handle_image_update("product", user_data['tenant'], product_code, image_status, image_data)
        await remember_users_action(user_data['user_id'], f"Product updated: {product_code}")

    return JSONResponse(content={
        "result": True,
        "code": product_code,
        "name": name
    })


@router.get("/search-products-list-get")
async def get_search_products_list(
        searchQuery: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Direct product search (code, name).
    """

    results = []
    product_code_pattern = re.fullmatch(r"(?i)p\d+", searchQuery)
    roll_code_pattern = re.fullmatch(r"(?i)p\d+r\d+", searchQuery)
    short_roll_code_pattern = re.fullmatch(r"(?i)r\d+", searchQuery)

    if roll_code_pattern:
        product_data = await get_product_and_roll_ps(searchQuery)
        if product_data:
            results.append(product_data)

    elif short_roll_code_pattern:
        # Roll code like R2; get roll and product.
        product_data = await get_roll_and_product_ps(searchQuery)
        if product_data:
            results.append(product_data)

    elif product_code_pattern:
        products = await search_products_list(searchQuery, 0)
        results = get_formatted_search_results_list(products, None)
    else:
        # name or general string
        products = await search_products_list(searchQuery, 1)
        results = get_formatted_search_results_list(products, None)

    return JSONResponse(content=results, status_code=200)


@router.get("/products-list-get")
async def get_products_list(
        stockCondition: int,
        category: int,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of products based on date and category.
    """
    products_data = await search_products_list_filtered(stockCondition, category)
    products_list = get_formatted_search_results_list(products_data, None)

    return JSONResponse(content=products_list, status_code=200)


@router.get("/product-and-roll-get")
async def get_product_and_roll(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    If *code* starts with “R” (roll code), call get_roll_and_product_ps;
    otherwise call get_product_and_roll_ps.
    """
    if code and code[0].upper() == "R":
        product = await get_roll_and_product_ps(code)
    else:
        product = await get_product_and_roll_ps(code)

    return JSONResponse(content=product, status_code=200)


@router.post("/remove-product")
async def remove_product(
        request: RemoveRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to either remove or archive a product.
    """
    if request.mode == "remove":
        result = await remove_product_ps(request.code)
        action_desc = f"Product removed with history: {request.code}"
        await handle_image_update("product", user_data['tenant'], request.code, "remove", None)
    elif request.mode == "archive":
        result = await archive_product_ps(request.code)
        action_desc = f"Product removed: {request.code}"
    else:
        await flatbed("debug", f"invalid mode {request.mode}")
        return JSONResponse(content={"error": "Invalid mode"}, status_code=400)

    if result:
        await remember_users_action(user_data['user_id'], action_desc)

    return JSONResponse(content={"result": result}, status_code=200)
