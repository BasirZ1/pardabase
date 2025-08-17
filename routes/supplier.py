from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse

from Models import RemoveSupplierRequest
from db import insert_new_supplier, remember_users_action, update_supplier, get_suppliers_list_ps, remove_supplier_ps, \
    get_supplier_details_ps, get_supplier_ps
from helpers import get_formatted_suppliers_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-supplier")
async def add_or_edit_supplier(
        idToEdit: Optional[int] = Form(None),
        name: str = Form(...),
        phone: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        notes: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    if idToEdit is None:
        # CREATE NEW
        supplier_id = await insert_new_supplier(name, phone, address, notes)
        if not supplier_id:
            return JSONResponse(content={
                "result": False,
                "name": name,
                "phone": phone
            })
        await remember_users_action(user_data['user_id'], f"Supplier Added: {name} {phone}")
    else:
        # UPDATE OLD
        supplier_id = await update_supplier(idToEdit, name, phone, address, notes)
        if not supplier_id:
            return JSONResponse(content={
                "result": False,
                "name": name,
                "phone": phone
            })
        await remember_users_action(user_data['user_id'], f"Supplier updated: {supplier_id},"
                                                          f" name: {name} phone: {phone}")
    return JSONResponse(content={
        "result": True,
        "id": supplier_id,
        "name": name,
        "phone": phone
    })


@router.get("/supplier-get")
async def get_supplier(
        supplierId: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a supplier based on supplier id.
    """
    supplier = await get_supplier_ps(supplierId)
    return JSONResponse(content=supplier, status_code=200)


@router.get("/supplier-details-get")
async def get_supplier_details(
        supplierId: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a supplier's details based on supplier id.
    """
    supplier_details = await get_supplier_details_ps(supplierId)
    return JSONResponse(content=supplier_details, status_code=200)


@router.get("/suppliers-list-get")
async def get_suppliers_list(
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of suppliers.
    """
    suppliers_data = await get_suppliers_list_ps()
    suppliers_list = get_formatted_suppliers_list(suppliers_data)
    return JSONResponse(content=suppliers_list, status_code=200)


@router.post("/remove-supplier")
async def remove_supplier(
        request: RemoveSupplierRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a supplier.
    """
    result = await remove_supplier_ps(request.supplierId)
    if result:
        await remember_users_action(user_data['user_id'], f"Supplier removed: {request.supplierId}")
    return JSONResponse(content={"result": result}, status_code=200)
