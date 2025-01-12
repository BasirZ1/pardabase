from utils.conn import get_connection


# The modified logs function
def flatbed(prefix, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO log (prefix, message)
    VALUES (%s, %s);""", (prefix, message, ))
    conn.commit()
    cur.close()
    conn.close()
