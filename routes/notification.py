from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db import get_notifications_for_user_ps
from helpers import get_formatted_notifications_list
from utils import verify_jwt_user, flatbed

router = APIRouter()
load_dotenv(override=True)

# TODO WEB PUSH IMP
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from pywebpush import webpush, WebPushException
# import os
#
#
# # Load your VAPID keys
# VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
# VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
# VAPID_CLAIMS = {
#     "sub": "mailto:your@email.com"
# }
#
#
# @router.get("/vapid_public_key")
# async def get_vapid_public_key():
#     return {"publicKey": VAPID_PUBLIC_KEY}
#
#
# @router.post("/subscribe")
# async def subscribe(request: Request):
#     body = await request.json()
#     subscriptions.append(body)  # Save in DB instead of memory
#     return {"message": "Subscribed"}
#
#
# @router.post("/send_notification")
# async def send_notification(request: Request):
#     body = await request.json()
#     payload = {
#         "title": body.get("title", "Notification"),
#         "body": body.get("body", "You have updates!")
#     }
#
#     failed = []
#     for sub in subscriptions:
#         try:
#             webpush(
#                 subscription_info=sub,
#                 data=str(payload),
#                 vapid_private_key=VAPID_PRIVATE_KEY,
#                 vapid_claims=VAPID_CLAIMS
#             )
#         except WebPushException as ex:
#             failed.append(sub)
#
#     return JSONResponse({"sent": len(subscriptions) - len(failed), "failed": len(failed)})


@router.get("/notifications-for-user-get")
async def get_notifications_for_user(
        oldSync: Optional[str] = None,
        user_data: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of notifications for user.
    """
    notifications_data = await get_notifications_for_user_ps(user_data['user_id'], user_data['level'], oldSync)
    notifications_list = get_formatted_notifications_list(notifications_data)
    return JSONResponse(content=notifications_list, status_code=200)
