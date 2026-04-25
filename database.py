import psycopg2
import os
import config

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # القنوات
    cur.execute("CREATE TABLE IF NOT EXISTS channels (channel_id TEXT PRIMARY KEY, user_id BIGINT)")
    # إعدادات اللغة
    cur.execute("CREATE TABLE IF NOT EXISTS user_settings (user_id BIGINT PRIMARY KEY, lang TEXT DEFAULT 'en')")
    # التفاعلات
    cur.execute("CREATE TABLE IF NOT EXISTS post_reactions (post_id TEXT, reaction_type TEXT, count INTEGER DEFAULT 0, PRIMARY KEY (post_id, reaction_type))")
    conn.commit()
    cur.close()
    conn.close()

def set_user_lang(user_id, lang):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_settings (user_id, lang) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET lang = EXCLUDED.lang", (user_id, lang))
    conn.commit()
    cur.close()
    conn.close()

def get_user_lang(user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT lang FROM user_settings WHERE user_id = %s", (user_id,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        return res[0] if res else "en"
    except: return "en"

def add_channel_to_db(channel_id, user_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO channels (channel_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (str(channel_id), user_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except: return False

def get_user_channels(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT channel_id FROM channels WHERE user_id = %s", (user_id,))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

init_db()
        
