from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse

from db import add_earning_to_user, remember_users_action, get_users_earning_history_ps
from helpers import get_formatted_earnings_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-user-earning")
async def add_user_earning(
        userId: str = Form(...),
        amount: int = Form(...),
        earningType: str = Form(...),
        reference: Optional[str] = Form(None),
        note: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    # EARNING RECORD
    username = await add_earning_to_user(userId, amount, earningType, reference, note, user_data['user_id'])
    if not username:
        return JSONResponse(content={
            "result": False,
        })
    await remember_users_action(user_data['user_id'], f"earning added for user: {username} -> "
                                                      f"{amount} {earningType} {reference}")
    return JSONResponse(content={
        "result": True
    })


@router.get("/earnings-history-get")
async def get_earnings_history(
        userId: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve earnings history based on userId.
    """
    earnings_data = await get_users_earning_history_ps(userId)
    earnings_list = get_formatted_earnings_list(earnings_data)

    return JSONResponse(content=earnings_list, status_code=200)
