from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db import get_notifications_for_user_ps
from helpers import get_formatted_notifications_list
from utils import verify_jwt_user, flatbed

router = APIRouter()
load_dotenv(override=True)


@router.get("/notifications-for-user-get")
async def get_notifications_for_user(
        oldSync: Optional[str] = None,
        user_data: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of notifications for user.
    """
    await flatbed("debug", f"here is oldSync {oldSync}, here is user_id {user_data['user_id']}, here is user_level {user_data['level']}")
    notifications_data = await get_notifications_for_user_ps(user_data['user_id'], user_data['level'], oldSync)
    await flatbed("debug", f"here are the results {str(notifications_data)}")
    notifications_list = get_formatted_notifications_list(notifications_data)
    return JSONResponse(content=notifications_list, status_code=200)
