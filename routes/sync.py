from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from Models import CheckSyncRequest, GetListsRequest
from db import get_sync, fetch_suppliers_list, fetch_salesmen_list, fetch_tailors_list, fetch_users_list, \
    fetch_entities_list
from helpers import format_date
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/check-sync")
async def check_sync(
        request: CheckSyncRequest,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Endpoint to check sync based on key.
    """
    last_sync = await get_sync(request.key)
    last_sync = format_date(last_sync)
    return JSONResponse(content=last_sync, status_code=200)


@router.post("/get-lists")
async def get_lists(
        request: GetListsRequest,
        _: dict = Depends(verify_jwt_user(required_level=2)),
):
    # Supported keys and their fetch functions
    list_fetchers = {
        "suppliers": fetch_suppliers_list,
        "salesmen": fetch_salesmen_list,
        "tailors": fetch_tailors_list,
        "users": fetch_users_list,
        "entities": fetch_entities_list
    }
    keys = request.keys
    # If "all" is requested, replace keys with all supported keys
    if "all" in keys:
        keys = list(list_fetchers.keys())

    invalid_keys = [k for k in keys if k not in list_fetchers]
    if invalid_keys:
        raise HTTPException(status_code=400, detail=f"Invalid list keys requested: {invalid_keys}")

    results = {}
    for key in keys:
        fetcher = list_fetchers[key]
        results[key] = await fetcher()

    return JSONResponse(content=results, status_code=200)
