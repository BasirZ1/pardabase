import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from utils import set_current_db
from utils.config import JWT_EXPIRY_MINUTES, REFRESH_EXPIRY_DAYS

load_dotenv(override=True)
SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()
ALGORITHM = "HS256"


def create_jwt_token(sub, username, full_name, level, tenant, image_url):
    payload = {
        "sub": sub,  # the user id
        "username": username,
        "full_name": full_name,
        "level": level,
        "tenant": tenant,  # for setting DB
        "image_url": image_url,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES),
        "type": "access"
    }

    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token


def create_refresh_token(sub, username, full_name, level, tenant, image_url):
    payload = {
        "sub": sub,  # the user id
        "username": username,
        "full_name": full_name,
        "level": level,
        "tenant": tenant,  # for setting DB
        "image_url": image_url,
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRY_DAYS),
        "type": "refresh"
    }

    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token


def verify_jwt_user(required_level: int):
    async def inner(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

            result = validate_payload(payload)

            if result['level'] < required_level:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            await set_db_from_tenant(result['tenant'])

            return result

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise HTTPException(status_code=401, detail="Invalid or expired access token")

    return inner


async def verify_refresh_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        result = validate_payload(payload)

        await set_db_from_tenant(result['tenant'])
        return result

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


async def set_db_from_tenant(tenant: str):
    """Dependency to set the current database."""
    if not tenant:
        raise HTTPException(status_code=400, detail="Missing tenant header")

    set_current_db(tenant)  # Just sets the DB, no return needed


#   HELPER
def validate_payload(payload: dict):
    sub = payload.get("sub")
    username = payload.get("username")
    full_name = payload.get("full_name")
    level = payload.get("level")
    tenant = payload.get("tenant")
    image_url = payload.get("image_url")

    if not sub or level is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": sub,
        "username": username,
        "full_name": full_name,
        "level": level,
        "tenant": tenant,
        "image_url": image_url
    }
