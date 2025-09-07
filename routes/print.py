from dotenv import load_dotenv
from fastapi import APIRouter, Depends

from redisdb import get_print_jobs_redis, mark_printed_redis, add_print_job_redis
from Models import AddPrintJobRequest, MarkPrintedRequest
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-print-job")
async def add_print_job(req: AddPrintJobRequest, user_data: dict = Depends(verify_jwt_user(required_level=2))):
    tenant = user_data["tenant"]
    job_id = await add_print_job_redis(tenant, req.fileName, req.fileContentBase64)
    return {"result": True, "job_id": job_id}


@router.get("/get-print-jobs")
async def get_print_jobs(
        since: int = 0,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    jobs = await get_print_jobs_redis(user_data['tenant'], since)
    return {"jobs": jobs}


@router.post("/mark-printed")
async def mark_printed(req: MarkPrintedRequest, user_data: dict = Depends(verify_jwt_user(required_level=3))):
    tenant = user_data["tenant"]
    await mark_printed_redis(tenant, req.job_id)
    return {"ok": True}
