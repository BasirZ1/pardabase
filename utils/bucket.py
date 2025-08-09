import asyncio
import os
import time
from PIL import Image
import io

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


# async def upload_image_to_r2(_type: str, tenant: str, code: str, image_data: bytes) -> str:
#     """
#     Uploads image to R2 using type, code and tenant name.
#     Converts image to WebP format.
#     Returns a cache-busted public URL.
#     """
#
#     img = Image.open(io.BytesIO(image_data))
#
#     if not img.format:
#         raise HTTPException(400, detail="Uploaded file is not a valid image.")
#
#     if img.width > 5000 or img.height > 5000:
#         raise HTTPException(400, detail="Image is too large.")
#
#     # Optional conversion — only convert if it's not already WebP
#     if img.format != "WEBP":
#         img = img.convert("RGB")
#         webp_buffer = io.BytesIO()
#         img.save(webp_buffer, format="WEBP", quality=85)
#         final_data = webp_buffer.getvalue()
#     else:
#         final_data = image_data  # already webp, just store it
#
#     version = int(time.time())
#     object_key = f"curtaindb/{tenant}/{_type}/pardaaf-{code}.webp"
#
#     loop = asyncio.get_event_loop()
#     await loop.run_in_executor(
#         None,
#         lambda: r2.put_object(
#             Bucket=R2_BUCKET_NAME,
#             Key=object_key,
#             Body=final_data,
#             ContentType='image/webp',
#             ACL='public-read'
#         )
#     )
#
#     return f"{object_key}?v={version}"


async def upload_image_to_r2(_type: str, tenant: str, code: str, image_data: bytes) -> str:
    """
    Uploads the 1200px image from client as-is.
    Generates and stores a 400px thumbnail and a 60x60 avatar.
    Returns the main image URL.
    """
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    version = int(time.time())
    base_key = f"curtaindb/{tenant}/{_type}/pardaaf-{code}"

    loop = asyncio.get_event_loop()

    # Upload original (already 1200px)
    await loop.run_in_executor(
        None,
        lambda: r2.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=f"{base_key}.webp",
            Body=image_data,
            ContentType='image/webp',
            ACL='public-read'
        )
    )

    # Generate 400px thumbnail
    thumb_400 = resize_image(img, 400)
    # Generate 60x60 avatar (square)
    avatar_60 = resize_image(img, 60, square=True)

    for suffix, data in [("_thumb", thumb_400), ("_60", avatar_60)]:
        await loop.run_in_executor(
            None,
            lambda s=suffix, d=data: r2.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=f"{base_key}{s}.webp",
                Body=d,
                ContentType='image/webp',
                ACL='public-read'
            )
        )

    return f"{base_key}.webp?v={version}"


# async def delete_image_from_r2(_type: str, tenant: str, code: str) -> bool:
#     object_key = f"curtaindb/{tenant}/{_type}/pardaaf-{code}.webp"
#     r2.delete_object(Bucket=R2_BUCKET_NAME, Key=object_key)
#     return True

async def delete_image_from_r2(_type: str, tenant: str, code: str) -> bool:
    base_key = f"curtaindb/{tenant}/{_type}/pardaaf-{code}"
    for suffix in ["", "_thumb", "_60"]:
        r2.delete_object(Bucket=R2_BUCKET_NAME, Key=f"{base_key}{suffix}.webp")
    return True


def resize_image(img: Image.Image, size: int, square: bool = False) -> bytes:
    resized = img.copy()

    if square:
        resized.thumbnail((size, size), Image.LANCZOS)
        canvas = Image.new("RGB", (size, size), (255, 255, 255))  # white padding
        offset = ((size - resized.width) // 2, (size - resized.height) // 2)
        canvas.paste(resized, offset)
        resized = canvas
    else:
        resized.thumbnail((size, size), Image.LANCZOS)

    buffer = io.BytesIO()
    resized.save(buffer, format="WEBP", quality=85)
    return buffer.getvalue()
