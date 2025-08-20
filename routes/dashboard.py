from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db import get_dashboard_data_ps, get_recent_activities_preview, search_recent_activities_list
from helpers import get_formatted_recent_activities_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.get("/")
async def index():
    return JSONResponse(content={"result": True}, status_code=200)


@router.post("/get-dashboard-data")
async def get_dashboard_data(
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    data = await get_dashboard_data_ps()
    activities_data = await get_recent_activities_preview()
    activities_list = get_formatted_recent_activities_list(activities_data)
    data["recentActivities"] = activities_list

    # Fetch data for the dashboard
    return JSONResponse(content=data, status_code=200)


@router.get("/recent-activities-list-get")
async def get_recent_activity(
        _date: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of recent activities.
    """
    recent_activity_data = await search_recent_activities_list(_date)
    recent_activities_list = get_formatted_recent_activities_list(recent_activity_data)

    return JSONResponse(content=recent_activities_list, status_code=200)
