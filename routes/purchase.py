from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse

from Models import RemovePurchaseRequest
from db import (remember_users_action, insert_new_purchase, update_purchase, remove_purchase_ps,
                archive_purchase_ps, insert_new_purchase_item, update_purchase_item,
                search_purchases_list_filtered, search_purchases_list_for_supplier, get_purchase_items_ps)
from helpers import format_timestamp, get_formatted_purchases_list, get_formatted_purchase_items
from utils import verify_jwt_user, flatbed

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-purchase")
async def add_or_edit_purchase(
        idToEdit: Optional[int] = Form(None),
        supplierId: int = Form(...),
        totalAmount: Optional[int] = Form(None),
        currency: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    if idToEdit is None:
        # CREATE NEW
        purchase_id, created_at, updated_at, created_by = await insert_new_purchase(
            supplierId, totalAmount, currency, description, user_data['user_id'])
        if not purchase_id:
            return JSONResponse(content={
                "result": False
            })
        await remember_users_action(user_data['user_id'], f"Purchase Added: "
                                                          f"{supplierId} {totalAmount} {currency} {description}")
    else:
        # UPDATE OLD
        created_at = None
        created_by = None
        purchase_id, updated_at = await update_purchase(idToEdit, supplierId, totalAmount, currency, description)
        if not purchase_id:
            return JSONResponse(content={
                "result": False
            })
        await remember_users_action(user_data['user_id'], f"Purchase updated: {purchase_id},"
                                                          f"{supplierId} {totalAmount} {currency} {description}")
    return JSONResponse(content={
        "result": True,
        "id": purchase_id,
        "createdAt": format_timestamp(created_at),
        "updatedAt": format_timestamp(updated_at),
        "createdBy": created_by
    })


@router.post("/add-or-edit-purchase-item")
async def add_or_edit_purchase_item(
        idToEdit: Optional[int] = Form(None),
        purchaseId: int = Form(...),
        productCode: str = Form(...),
        costPerMetre: int = Form(...),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    if idToEdit is None:
        # CREATE NEW
        purchase_item_id = await insert_new_purchase_item(
            purchaseId, productCode, costPerMetre)
        if not purchase_item_id:
            return JSONResponse(content={
                "result": False
            })
        await remember_users_action(user_data['user_id'], f"Purchase Item Added: "
                                                          f"{purchase_item_id} {purchaseId}"
                                                          f" {productCode} {costPerMetre}")
    else:
        # UPDATE OLD
        purchase_item_id = await update_purchase_item(idToEdit, purchaseId, productCode, costPerMetre)
        if not purchase_item_id:
            return JSONResponse(content={
                "result": False
            })
        await remember_users_action(user_data['user_id'], f"Purchase Item updated: {purchase_item_id},"
                                                          f"{purchaseId} {productCode} {costPerMetre}")
    return JSONResponse(content={
        "result": True,
        "id": purchase_item_id
    })


@router.get("/purchases-list-get")
async def get_purchases_list(
        date: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of purchases based on date.
    """
    purchases_data = await search_purchases_list_filtered(date)
    purchases_list = get_formatted_purchases_list(purchases_data)

    return JSONResponse(content=purchases_list, status_code=200)


@router.get("/purchases-list-for-supplier-get")
async def get_purchases_list_for_supplier(
        supplierId: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of purchases based on supplierId.
    """
    purchases_data = await search_purchases_list_for_supplier(supplierId)
    purchases_list = get_formatted_purchases_list(purchases_data)

    return JSONResponse(content=purchases_list, status_code=200)


@router.get("/purchase-items-get")
async def get_purchase_items(
        purchaseId: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve purchase items for a particular purchase.
    """
    purchase_items_data = await get_purchase_items_ps(purchaseId)
    purchase_items = get_formatted_purchase_items(purchase_items_data)

    return JSONResponse(content=purchase_items, status_code=200)


@router.post("/remove-purchase")
async def remove_purchase(
        request: RemovePurchaseRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to either remove or archive a purchase.
    """
    if request.mode == "remove":
        result = await remove_purchase_ps(request.purchaseId)
        action_desc = f"Purchase removed with history: {request.purchaseId}"
    elif request.mode == "archive":
        result = await archive_purchase_ps(request.purchaseId)
        action_desc = f"Purchase removed: {request.purchaseId}"
    else:
        await flatbed("debug", f"invalid mode {request.mode}")
        return JSONResponse(content={"error": "Invalid mode"}, status_code=400)

    if result:
        await remember_users_action(user_data['user_id'], action_desc)

    return JSONResponse(content={"result": result}, status_code=200)
