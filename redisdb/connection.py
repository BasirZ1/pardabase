import os

import redis.asyncio as redis
from redis.exceptions import RedisError
from dotenv import load_dotenv

load_dotenv(override=True)


_redis_singletons = {}


async def get_redis_connection(decode_responses: bool = True):
    """
    Get a shared async Redis connection.
    Creates it once and reuses it.
    """
    global _redis_singletons
    key = "str" if decode_responses else "bytes"

    if key in _redis_singletons:
        return _redis_singletons[key]

    try:
        red_host = os.getenv("RED_HOST", "localhost")
        red_port = int(os.getenv("RED_PORT", 6379))
        red_user = os.getenv("RED_USER", "default")
        red_password = os.getenv("RED_PASSWORD")

        r = redis.Redis(
            host=red_host,
            port=red_port,
            db=1,
            username=red_user,
            password=red_password,
            socket_timeout=5,
            socket_connect_timeout=2,
            decode_responses=decode_responses
        )
        await r.ping()
        print(f"Connected to Redis (decode_responses={decode_responses})")

        _redis_singletons[key] = r
        return r
    except RedisError as e:
        print(f"Redis error: {e}")
        raise e


async def close_redis_connections():
    for client in _redis_singletons.values():
        await client.close()
    _redis_singletons.clear()
