from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse

from Models import AddExpenseRequest, RemoveExpenseRequest
from db import insert_new_expense, remember_users_action, update_expense, search_expenses_list_filtered, \
    remove_expense_ps
from helpers import get_formatted_expenses_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-expense")
async def add_expense(
        request: AddExpenseRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to add an expense.
    """
    expense_id = await insert_new_expense(request.categoryIndex, request.description, request.amount)
    if expense_id:
        await remember_users_action(user_data['user_id'], f"Added Expense: Desc: {request.description}")
        return JSONResponse(content={
            "description": request.description,
            "amount": request.amount
        })
    return "Failure", 500


@router.post("/add-or-edit-expense")
async def add_or_edit_expense(
        categoryIndex: int = Form(...),
        amount: int = Form(...),
        description: Optional[str] = Form(None),
        idToEdit: Optional[int] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    if idToEdit is None:
        # CREATE NEW
        _id = await insert_new_expense(categoryIndex, description, amount)
        if not id:
            return JSONResponse(content={
                "result": False,
                "description": description,
                "amount": amount
            })
        await remember_users_action(user_data['user_id'], f"Expense Added: {description} {amount}")
    else:
        # UPDATE OLD
        _id = await update_expense(idToEdit, categoryIndex, description, amount)
        if not _id:
            return JSONResponse(content={
                "result": False,
                "description": description,
                "amount": amount
            })
        await remember_users_action(user_data['user_id'], f"Expense updated: {_id},"
                                                          f" description: {description} amount: {amount}")
    return JSONResponse(content={
        "result": True,
        "description": description,
        "amount": amount
    })


@router.get("/expenses-list-get")
async def get_expenses_list(
        date: int,
        category: int,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of expenses based on date and category.
    """
    expenses_data = await search_expenses_list_filtered(date, category)
    expenses_list = get_formatted_expenses_list(expenses_data)
    return JSONResponse(content=expenses_list, status_code=200)


@router.post("/remove-expense")
async def remove_expense(
        request: RemoveExpenseRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove an expense.
    """
    result = await remove_expense_ps(request.expenseId)
    if result:
        await remember_users_action(user_data['user_id'], f"Expense removed: {request.expenseId}")
    return JSONResponse(content={"result": result}, status_code=200)