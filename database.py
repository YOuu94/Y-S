def delete_channel_from_db(channel_id):
    """حذف قناة من قاعدة البيانات"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("DELETE FROM channels WHERE channel_id = %s", (channel_id,))
        conn.commit()
        cur.close()
        return True
    except:
        return False
    finally:
        if conn: conn.close()
