from Models.pydantic_models import BotState
from redisdb.connection import get_redis_connection
from utils.config import STATE_TTL_SECONDS


async def get_user_state(chat_id: int) -> str:
    r = await get_redis_connection()
    state = await r.get(f"user_state:{chat_id}")
    return state if state is not None else BotState.IDLE


async def set_user_state(chat_id: int, state: str):
    r = await get_redis_connection()
    await r.set(f"user_state:{chat_id}", state, ex=STATE_TTL_SECONDS)
