from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse

from Models import CodeRequest, UpdateBillStatusRequest, UpdateBillTailorRequest, AddPaymentBillRequest
from db import insert_new_bill, remember_users_action, update_bill, get_bill_ps, search_bills_list_filtered, \
    remove_bill_ps, update_bill_status_ps, update_bill_tailor_ps, add_payment_bill_ps, get_payment_history_ps
from helpers import get_formatted_search_results_list
from telegram import notify_if_applicable
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-bill")
async def add_or_edit_bill(
        codeToEdit: Optional[str] = Form(None),
        billDate: Optional[str] = Form(None),
        dueDate: Optional[str] = Form(None),
        customerName: Optional[str] = Form(None),
        customerNumber: Optional[str] = Form(None),
        price: Optional[int] = Form(None),
        paid: Optional[int] = Form(None),
        remaining: Optional[int] = Form(None),
        status: Optional[str] = Form(None),
        fabrics: Optional[str] = Form(None),
        parts: Optional[str] = Form(None),
        salesman: Optional[str] = Form(None),
        tailor: Optional[str] = Form(None),
        additionalData: Optional[str] = Form(None),
        installation: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    if codeToEdit is None:
        # CREATE NEW
        code = await insert_new_bill(billDate, dueDate, customerName, customerNumber, price, paid, remaining, status,
                                     fabrics, parts, salesman, tailor, additionalData, installation)
        if not code:
            return JSONResponse(content={
                "result": False,
                "code": code,
                "name": customerName
            })
        await remember_users_action(user_data['user_id'], f"Bill Added: {code}")
    else:
        # UPDATE OLD
        code = await update_bill(codeToEdit, dueDate, customerName, customerNumber, price, paid, remaining, status,
                                 fabrics, parts, salesman, tailor, additionalData, installation, user_data['username'])
        if not code:
            return JSONResponse(content={
                "result": False,
                "code": code,
                "name": customerName
            })
        await remember_users_action(user_data['user_id'], f"Bill updated: {code}")
    return JSONResponse(content={
        "result": True,
        "code": code,
        "name": customerName
    })


@router.get("/bill-get")
async def get_bill(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a bill based on code.
    """
    bill = await get_bill_ps(code)
    return JSONResponse(content=bill, status_code=200)


@router.get("/bills-list-get")
async def get_bills_list(
        date: int,
        state: int,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of bills based on date or state.
    """
    bills_data = await search_bills_list_filtered(date, state)
    bills_list = get_formatted_search_results_list(None, bills_data)

    return JSONResponse(content=bills_list, status_code=200)


@router.post("/add-payment-bill")
async def add_payment_bill(
        request: AddPaymentBillRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to update a bill's payment.
    """
    result = await add_payment_bill_ps(request.code, request.amount, user_data['username'])
    await remember_users_action(user_data['user_id'], f"Added payment to bill: "
                                                      f"{request.code} {request.amount}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.get("/bill-payment-history-get")
async def get_bill_payment_history(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve bill payment_history based on code.
    """
    payment_history = await get_payment_history_ps(code)
    return JSONResponse(content=payment_history, status_code=200)


@router.post("/update-bill-status")
async def update_bill_status(
        request: UpdateBillStatusRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to update a bill's status.
    """
    previous_status = await update_bill_status_ps(request.code, request.status)
    result = previous_status is not None
    if result:
        await notify_if_applicable(request.code, previous_status, request.status)
        await remember_users_action(user_data['user_id'], f"Bill status updated: "
                                                          f"{request.code} from {previous_status} to {request.status}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/update-bill-tailor")
async def update_bill_tailor(
        request: UpdateBillTailorRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to update a bill's tailor.
    """
    updated_tailor_name = await update_bill_tailor_ps(request.code, request.tailor)
    await remember_users_action(user_data['user_id'], f"Bill's tailor updated: "
                                                      f"{request.code} {updated_tailor_name}")
    result = updated_tailor_name is not None
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/remove-bill")
async def remove_bill(
        request: CodeRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a bill.
    """
    result = await remove_bill_ps(request.code)
    if result:
        await remember_users_action(user_data['user_id'], f"Bill removed: {request.code}")
    return JSONResponse(content={"result": result}, status_code=200)
