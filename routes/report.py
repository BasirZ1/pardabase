from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from Models import GenerateReportRequest
from db import remember_users_action, report_recent_activities_list, \
    report_tags_list
from helpers import get_formatted_recent_activities_list, get_formatted_tags_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/generate-report")
async def generate_report(
        request: GenerateReportRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to generate various reports.
    """
    data = None
    if request.selectedReport == "activities":
        recent_activity_data = await report_recent_activities_list(request.fromDate, request.toDate)
        data = get_formatted_recent_activities_list(recent_activity_data)
    elif request.selectedReport == "tags":
        tags_data = await report_tags_list(request.fromDate, request.toDate)
        data = get_formatted_tags_list(tags_data)
    await remember_users_action(user_data['user_id'], f"generated Report: "
                                                      f"{request.selectedReport}"
                                                      f" from {request.fromDate} to {request.toDate}")
    return JSONResponse(content=data, status_code=200)
