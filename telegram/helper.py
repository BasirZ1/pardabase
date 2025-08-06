from db import get_gallery_db_name, check_username_and_set_chat_id, check_bill_status_ps
from .notify import send_notification
from utils import set_current_db


def get_text_according_to_message_text(message_text):
    if message_text == "/start":
        return ("Welcome to parda.af bot!"
                "\nGo to parda.af for our curtains collection or use /inform, /link or /checkbillstatus.")
    elif message_text == "/link":
        return "Please send your username@gallery_codename to link your account."
    elif message_text == "/checkbillstatus":
        return "Send the bill_number@gallery_code_name. We will check it's status and inform you."
    elif message_text == "/inform":
        return "Send the bill_number@gallery_code_name. We will inform you when it has been tailored."
    else:
        return ("Unrecognized command."
                "\nGo to parda.af for our curtains collection or use /inform, /link or /checkbillstatus.")


async def perform_linking_telegram_to_username(message_text, chat_id):
    if '@' not in message_text or message_text.count('@') != 1:
        await send_notification(chat_id, "❌ Invalid format. Please send username@gallery_codename.")
        return {"ok": True}

    username, gallery_codename = message_text.split('@')
    if not username or not gallery_codename:
        await send_notification(chat_id, "❌ Both username and gallery codename must be provided.")
        return {"ok": True}

    set_current_db("pardaaf_main")
    gallery_db_name = await get_gallery_db_name(gallery_codename)
    if not gallery_db_name:
        await send_notification(chat_id, "❌ Failed to link your Telegram account.")
        return {"ok": True}
    set_current_db(gallery_db_name)
    success = await check_username_and_set_chat_id(username, chat_id)
    if success:
        await send_notification(chat_id, "✅ Your Telegram account has been successfully linked!")
    else:
        await send_notification(chat_id, "❌ Failed to link your Telegram account.")


async def perform_bill_check(message_text, chat_id):
    if '@' not in message_text or message_text.count('@') != 1:
        await send_notification(chat_id, "❌ Invalid format. Please send bill_number@gallery_code_name.")
        return {"ok": True}

    bill_code, gallery_codename = message_text.split('@')
    if not bill_code or not gallery_codename:
        await send_notification(chat_id, "❌ Both bill_number and gallery codename must be provided.")
        return {"ok": True}

    set_current_db("pardaaf_main")
    gallery_db_name = await get_gallery_db_name(gallery_codename)
    if not gallery_db_name:
        await send_notification(chat_id, "❌ Gallery code name is incorrect.")
        return {"ok": True}
    set_current_db(gallery_db_name)
    status = await check_bill_status_ps(bill_code)
    if status:
        if status == "pending" or status == "cut":
            await send_notification(chat_id, f"The {bill_code} bill is pending. Please wait!")
        elif status == "with_tailor":
            await send_notification(chat_id, f"The {bill_code} bill is under work. Please wait!")
        elif status == "ready":
            await send_notification(chat_id, f"The {bill_code} bill is ready. You can pick it up!")
        elif status == "delivered":
            await send_notification(chat_id, f"The {bill_code} bill has been delivered successfully")
    else:
        await send_notification(chat_id, "❌ Failed to link your Telegram account.")
