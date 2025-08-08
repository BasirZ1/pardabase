import json

from redisdb.connection import get_redis_connection


async def get_next_job_id(tenant: str) -> int:
    r = await get_redis_connection()
    return await r.incr(f"tenant:last_job_id:{tenant}")


async def add_print_job_redis(tenant: str, file_name: str, file_content_base64: str) -> int:
    r = await get_redis_connection()
    job_id = await get_next_job_id(tenant)
    job = {
        "id": job_id,
        "file_name": file_name,
        "file_content_base64": file_content_base64,
        "tenant": tenant,
    }
    await r.rpush(f"tenant:print_jobs:{tenant}", json.dumps(job))
    return job_id


async def get_print_jobs_redis(tenant: str, since: int = 0):
    r = await get_redis_connection()
    jobs_json = await r.lrange(f"tenant:print_jobs:{tenant}", 0, -1)
    jobs = [json.loads(j) for j in jobs_json]
    # Filter jobs with id > since
    return [job for job in jobs if job["id"] > since]


async def mark_printed_redis(tenant: str, job_id: int):
    r = await get_redis_connection()
    key = f"tenant:print_jobs:{tenant}"
    jobs_json = await r.lrange(key, 0, -1)
    for job_json in jobs_json:
        job = json.loads(job_json)
        if job["id"] == job_id:
            await r.lrem(key, 1, job_json)
            break
