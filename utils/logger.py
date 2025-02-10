from utils.email_sender import send_mail
from utils.config import ADMIN_EMAIL
from utils.conn import get_connection


# The modified logs function
def flatbed(prefix, message):
    send_mail(f"{prefix}", ADMIN_EMAIL, message)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO log (prefix, message)
    VALUES (%s, %s);""", (prefix, message, ))
    conn.commit()
    cur.close()
    conn.close()
