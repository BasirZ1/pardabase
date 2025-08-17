from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.requests import Request

from Models import BotState
from redisdb import get_user_state, set_user_state
from telegram import get_text_according_to_message_text, send_notification, perform_linking_telegram_to_username, \
    handle_bill_status
from utils.config import STATE_CHANGING_COMMANDS

router = APIRouter()
load_dotenv(override=True)


@router.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return {"ok": True}

    state = await get_user_state(chat_id)

    message_text = message.get("text", "").strip()
    if not message_text:
        return {"ok": True}

    reply_text = get_text_according_to_message_text(message_text)
    normalized_text = message_text.lower()

    if normalized_text.startswith("/start"):
        await set_user_state(chat_id, BotState.IDLE)
        await send_notification(chat_id, reply_text)
    elif normalized_text.startswith("/link"):
        await set_user_state(chat_id, BotState.AWAITING_USERNAME)
        await send_notification(chat_id, reply_text)
    elif normalized_text.startswith("/checkbillstatus"):
        await set_user_state(chat_id, BotState.AWAITING_BILL_CHECK)
        await send_notification(chat_id, reply_text)
    elif normalized_text.startswith("/notify"):
        await set_user_state(chat_id, BotState.AWAITING_BILL_NUMBER)
        await send_notification(chat_id, reply_text)
    elif state == BotState.AWAITING_USERNAME:
        await perform_linking_telegram_to_username(message_text, chat_id)
    elif state == BotState.AWAITING_BILL_CHECK:
        await handle_bill_status(message_text, chat_id)
    elif state == BotState.AWAITING_BILL_NUMBER:
        await handle_bill_status(message_text, chat_id, should_save=True)
    else:
        await send_notification(chat_id, reply_text)

    if not any(normalized_text.startswith(cmd) for cmd in STATE_CHANGING_COMMANDS):
        await set_user_state(chat_id, BotState.IDLE)
