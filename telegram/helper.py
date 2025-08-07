from db import get_gallery_db_name, check_username_and_set_chat_id, check_bill_status_ps, save_notify_bill_status_ps
from .notify import send_notification
from utils import set_current_db


def get_text_according_to_message_text(message_text):
    if message_text == "/start":
        return (
            "👋 Welcome to the *Parda.af* bot!"
            "\nVisit [parda.af](https://parda.af) to explore our curtain collection."
            "\nUse /notify to get notified when your bill is ready, or /checkbillstatus to check your bill's status."
        )
    elif message_text == "/link":
        return "🔗 To link your account, send: `your_username@gallery_codename`"
    elif message_text == "/checkbillstatus":
        return "📋 To check your bill status, send: `bill_number@gallery_codename`"
    elif message_text == "/notify":
        return "🔔 To get notified when your bill is ready, send: `bill_number@gallery_codename`"
    else:
        return (
            "❌ Unrecognized command."
            "\nVisit [parda.af](https://parda.af) to explore our curtain collection."
            "\nUse /notify or /checkbillstatus to manage your orders."
        )


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


async def handle_bill_status(message_text: str, chat_id: str, should_save=False):
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
    bill_code = bill_code.upper()
    status = await check_bill_status_ps(bill_code)

    if not status:
        await send_notification(chat_id, "❌ Bill not found! Check your bill_number@gallery_code_name and try again.")
        return {"ok": True}

    notify_text = ""
    if status in {"pending", "cut"}:
        if should_save:
            await save_notify_bill_status_ps(chat_id, bill_code)
            notify_text = f"🕓 The {bill_code} bill is pending. We'll notify you when it's ready."
        else:
            notify_text = f"🕓 The {bill_code} bill is pending. Please wait!"
    elif status == "with_tailor":
        if should_save:
            await save_notify_bill_status_ps(chat_id, bill_code)
            notify_text = f"🧵 The {bill_code} bill is under tailoring. We'll notify you when it's ready."
        else:
            notify_text = f"🧵 The {bill_code} bill is under tailoring. Please wait!"
    elif status == "ready":
        notify_text = f"✅ The {bill_code} bill is ready! You can pick it up now."
    elif status == "delivered":
        notify_text = f"📦 The {bill_code} bill has been delivered."
    elif status == "canceled":
        notify_text = f"❌ The {bill_code} bill was canceled. Contact us if you have concerns."

    await send_notification(chat_id, notify_text)
    return {"ok": True}
