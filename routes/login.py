from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from Models import RefreshTokenRequest, AuthRequest, ChangePasswordRequest
from db import get_users_data, check_username_password, update_users_password
from utils import verify_refresh_token, create_jwt_token, create_refresh_token, set_db_from_tenant, verify_jwt_user
from utils.hasher import hash_password

router = APIRouter()
load_dotenv(override=True)


@router.post("/login")
async def login(
        request: AuthRequest
):
    await set_db_from_tenant(request.tenant)

    check_result = await check_username_password(request.username, request.password)

    if check_result:
        data = await get_users_data(request.username)

        user_id = data["user_id"]
        full_name = data["full_name"]
        username = request.username.lower()
        level = data["level"]
        image_url = data["image_url"]

        access_token = create_jwt_token(user_id, username, level,
                                        request.tenant)
        _refresh_token = create_refresh_token(user_id, username, level,
                                              request.tenant)

        return JSONResponse(content={
            "accessToken": access_token,
            "refreshToken": _refresh_token,
            "userId": user_id,
            "fullName": full_name,
            "level": level,
            "imageUrl": image_url
        }, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    user_data = await verify_refresh_token(request.refreshToken)

    data = await get_users_data(user_data['username'])

    user_id = data["user_id"]
    full_name = data["full_name"]
    level = data["level"]
    image_url = data["image_url"]

    # Create new access and refresh tokens
    new_access_token = create_jwt_token(
        sub=user_id,
        username=user_data['username'],
        level=level,
        tenant=user_data['tenant']
    )

    new_refresh_token = create_refresh_token(
        sub=user_id,
        username=user_data['username'],
        level=level,
        tenant=user_data['tenant']
    )

    return JSONResponse(content={
        "accessToken": new_access_token,
        "refreshToken": new_refresh_token,
        "userId": user_id,
        "fullName": full_name,
        "level": level,
        "imageUrl": image_url
    }, status_code=200)


@router.post("/change-password")
async def change_password(
        request: ChangePasswordRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Endpoint to change password for Admin accounts.
    """
    old_password = request.oldPassword
    new_password = request.newPassword

    check_old_password = await check_username_password(user_data['username'], old_password)
    if check_old_password is False:
        return JSONResponse(content={"result": False}, status_code=200)

    await update_users_password(user_data['username'], hash_password(new_password))
    return JSONResponse(content={"result": True}, status_code=200)
