import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from utils import set_current_db
from utils.config import JWT_EXPIRY_MINUTES

load_dotenv(override=True)
SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()


async def create_jwt_token(data, username, tenant):
    payload = {
        "sub": data['user_id'],  # the user id
        "username": username,
        "full_name": data['full_name'],
        "level": data['level'],
        "tenant": tenant,  # for setting DB
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt_user(required_level: int):
    async def inner(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            sub = payload.get("sub")
            username = payload.get("username")
            full_name = payload.get("full_name")
            level = payload.get("level")
            tenant = payload.get("tenant")

            if not sub or level is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

            if level < required_level:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

            await set_db_from_tenant(tenant)

            return {"user_id": sub, "username": username, "full_name": full_name, "level": level}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return inner


async def set_db_from_tenant(tenant: str):
    """Dependency to set the current database."""
    if not tenant:
        raise HTTPException(status_code=400, detail="Missing tenant header")

    set_current_db(tenant)  # Just sets the DB, no return needed
