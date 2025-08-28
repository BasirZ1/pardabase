from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse

from db import add_payment_to_user, remember_users_action, add_payment_to_supplier, add_payment_to_entity, \
    insert_new_expense, get_user_payment_history_ps, get_supplier_payment_history_ps
from helpers import get_expense_cat_name, get_formatted_payments_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-payment")
async def add_payment(
        paymentType: Optional[str] = Form(None),
        supplierId: Optional[int] = Form(None),
        userId: Optional[str] = Form(None),
        entityId: Optional[int] = Form(None),
        expenseCat: Optional[str] = Form(None),
        amount: Optional[int] = Form(None),
        currency: Optional[str] = Form(None),
        note: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    expense_cat_id = None
    expense_note = note or ""

    if paymentType == "user":
        username = await add_payment_to_user(userId, amount, currency, note, user_data['user_id'])
        if not username:
            return JSONResponse(content={"result": False})
        await remember_users_action(user_data['user_id'], f"Payment added to user: {username}")

        expense_cat_id = 1
        expense_note = f"[User: {username}] {expense_note}"

    elif paymentType == "supplier":
        supplier_name = await add_payment_to_supplier(supplierId, amount, currency, note, user_data['user_id'])
        if not supplier_name:
            return JSONResponse(content={"result": False})
        await remember_users_action(user_data['user_id'], f"Payment added to supplier: {supplier_name}")

        expense_cat_id = 0
        expense_note = f"[Supplier: {supplier_name}] {expense_note}"

    elif paymentType == "entity":
        entity_name = await add_payment_to_entity(entityId, amount, currency, note, user_data['user_id'])
        if not entity_name:
            return JSONResponse(content={"result": False})
        await remember_users_action(user_data['user_id'], f"Payment added to entity: {entity_name}")

        expense_cat_id = 7
        expense_note = f"[Entity: {entity_name}] {expense_note}"

    elif paymentType == "expense":
        expense_cat_id = expenseCat

    # Save expense if category decided
    if expense_cat_id is not None:
        expense_id = await insert_new_expense(expense_cat_id, expense_note, amount, currency, user_data['user_id'])
        if not expense_id:
            return JSONResponse(content={"result": False})
        expense_cat_name = get_expense_cat_name(str(expense_cat_id))
        await remember_users_action(
            user_data['user_id'],
            f"Expense added: {expense_cat_name} {expense_note} {amount} {currency}"
        )

    return JSONResponse(content={"result": True})


@router.get("/payment-history-get")
async def get_payment_history(
        paymentType: str,
        partyValue: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve payment_history based on paymentType and partyValue.
    """
    if paymentType == "user":
        payments_data = await get_user_payment_history_ps(partyValue)
        payments_history = get_formatted_payments_list(payments_data)
    elif paymentType == "supplier":
        payments_data = await get_supplier_payment_history_ps(int(partyValue))
        payments_history = get_formatted_payments_list(payments_data)
    else:
        payments_history = []
    return JSONResponse(content=payments_history, status_code=200)
