ADMIN_EMAIL = 'developers@basirsoft.com'
ADMIN_TELEGRAM = '7666061191'
JWT_EXPIRY_MINUTES = 360
REFRESH_EXPIRY_DAYS = 90

# State management with auto-cleanup (states expire after 1 hour) -- for telegram users
STATE_TTL_SECONDS = 3600
STATE_CHANGING_COMMANDS = ["/link", "/checkbillstatus", "/notify"]

# --- Local normalization ---
AFN_ADJUSTMENT = 0.025  # 2.5% lower than open FX
