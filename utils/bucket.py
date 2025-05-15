import asyncio
import os
import time

import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv(override=True)

# Replace with your actual values
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = "basirsoft"
R2_REGION = "eeur"
R2_ENDPOINT = f"https://{CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"

session = boto3.session.Session()
r2 = session.client(
    service_name='s3',
    region_name=R2_REGION,
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version='s3v4', retries={'max_attempts': 1})
)


async def upload_image_to_r2(_type: str, tenant: str, code: str, image_data: bytes) -> str:
    """
    Uploads image to R2 using type, code and tenant name.
    Returns a cache-busted public URL.
    """

    version = int(time.time())
    object_key = f"curtaindb/{tenant}/{_type}/pardaaf-{code}.jpg"

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: r2.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=object_key,
            Body=image_data,
            ContentType='image/jpeg',
            ACL='public-read'
        )
    )

    return f"{object_key}?v={version}"


async def delete_image_from_r2(_type: str, tenant: str, code: str) -> bool:
    """
    Deletes an image from R2 using type, code and tenant name.
    Returns True if successful, False otherwise.
    """
    object_key = f"curtaindb/{tenant}/{_type}/pardaaf-{code}.jpg"

    r2.delete_object(Bucket=R2_BUCKET_NAME, Key=object_key)
    return True
