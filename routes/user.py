from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse

from Models import RemoveUserRequest
from db import remove_user_ps, handle_image_update, remember_users_action, insert_new_user, update_user, \
    get_users_list_ps, edit_employment_info_ps, get_profile_data_ps, get_employment_info_ps
from helpers import classify_image_upload, get_formatted_users_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-user")
async def add_or_edit_user(
        usernameToEdit: Optional[str] = Form(None),
        fullName: str = Form(...),
        usernameChange: str = Form(...),
        password: Optional[str] = Form(None),
        level: int = Form(...),
        image: Optional[UploadFile] = File(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    image_status, image_data = await classify_image_upload(image)

    if usernameToEdit is None:
        # CREATE NEW
        if password is None:
            return JSONResponse(content={"error": "Password is missing"}, status_code=403)
        user_id = await insert_new_user(fullName, usernameChange, password, level)
        if not user_id:
            return JSONResponse(content={"result": False}, status_code=201)
        await handle_image_update("user", user_data['tenant'], usernameChange, image_status, image_data)
        await remember_users_action(user_data['user_id'], f"User added: {usernameChange}")
    else:
        user_id = await update_user(usernameToEdit, fullName, usernameChange, level, password)
        if not user_id:
            return JSONResponse(content={"result": False}, status_code=201)
        await handle_image_update("user", user_data['tenant'], usernameChange, image_status, image_data)
        await remember_users_action(user_data['user_id'], f"user updated: {usernameChange}")

    return JSONResponse(content={
        "result": True,
        "userId": user_id
    }, status_code=200)


@router.post("/edit-employment-info")
async def edit_employment_info(
        userId: Optional[str] = Form(None),
        salaryAmount: Optional[int] = Form(None),
        salaryStartDate: Optional[str] = Form(None),
        salaryCycle: Optional[str] = Form(None),
        tailorType: Optional[str] = Form(None),
        salesmanStatus: Optional[str] = Form(None),
        billBonusPercent: Optional[int] = Form(None),
        note: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    # UPDATE OLD
    username = await edit_employment_info_ps(userId, salaryAmount, salaryStartDate, salaryCycle, tailorType, salesmanStatus,
                                             billBonusPercent, note)
    if not username:
        return JSONResponse(content={
            "result": False,
        })
    await remember_users_action(user_data['user_id'], f"Employment info updated: {username}")
    return JSONResponse(content={
        "result": True,
        "username": username
    })


@router.get("/profile-data-get")
async def get_profile_data(
        userId: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve profile data based on userId.
    """
    profile_data = await get_profile_data_ps(userId)
    return JSONResponse(content=profile_data, status_code=200)


@router.get("/employment-info-get")
async def get_employment_info(
        userId: str,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve employment info based on userId.
    """
    employment_info = await get_employment_info_ps(userId)
    return JSONResponse(content=employment_info, status_code=200)


@router.get("/users-list-get")
async def get_users_list(
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of users.
    """
    users_data = await get_users_list_ps()
    users_list = get_formatted_users_list(users_data)
    return JSONResponse(content=users_list, status_code=200)


@router.post("/remove-user")
async def remove_user(
        request: RemoveUserRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a user.
    """
    result = await remove_user_ps(request.usernameToRemove)
    if result:
        await handle_image_update("user", user_data['tenant'], request.usernameToRemove, "remove", None)
        await remember_users_action(user_data['user_id'], f"User removed: {request.usernameToRemove}")
    return JSONResponse(content={"result": result}, status_code=200)
