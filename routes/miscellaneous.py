from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse

from db import add_miscellaneous_record_ps, remember_users_action, search_miscellaneous_records
from helpers import get_formatted_misc_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-miscellaneous-record")
async def add_miscellaneous_record(
        amount: int = Form(...),
        currency: str = Form(...),
        direction: str = Form(...),
        supplierId: Optional[int] = Form(None),
        entityId: Optional[int] = Form(None),
        transactionType: Optional[str] = Form(None),
        note: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    # MISC RECORD
    name = await add_miscellaneous_record_ps(amount, currency, direction, supplierId,
                                             entityId, transactionType, note, user_data['user_id'])
    if not name:
        return JSONResponse(content={
            "result": False,
        })
    await remember_users_action(user_data['user_id'], f"miscellaneous record added: {direction} -> "
                                                      f"{name} {amount} {currency} {transactionType}")
    return JSONResponse(content={
        "result": True
    })


@router.get("/miscellaneous-records-history-get")
async def get_miscellaneous_records_history(
        recordId: int,
        recordType: str,
        direction: str,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve miscellaneous records based on id (supplier_id, entity_id) and type (supplier, entity).
    """
    misc_records_data = await search_miscellaneous_records(recordId, recordType, direction)
    misc_list = get_formatted_misc_list(misc_records_data)

    return JSONResponse(content=misc_list, status_code=200)
