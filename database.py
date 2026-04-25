import psycopg2
import os
import config

# جلب رابط قاعدة البيانات وتصحيحه ليتوافق مع مكتبة psycopg2
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_connection():
    """إنشاء اتصال جديد بقاعدة البيانات"""
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """إنشاء الجداول اللازمة عند تشغيل البوت لأول مرة"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # جدول القنوات المرتبطة (مع شرط عدم التكرار)
        cur.execute('''CREATE TABLE IF NOT EXISTS channels (
                        channel_id TEXT PRIMARY KEY, 
                        user_id BIGINT
                    )''')
        
        # جدول المشرفين
        cur.execute('''CREATE TABLE IF NOT EXISTS admins (
                        user_id BIGINT PRIMARY KEY
                    )''')
        
        # إضافة المطور كأدمن افتراضي
        cur.execute("INSERT INTO admins (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (config.OWNER_ID,))
        
        conn.commit()
        cur.close()
        print("✅ تم تجهيز قاعدة البيانات PostgreSQL بنجاح")
    except Exception as e:
        print(f"❌ خطأ أثناء تهيئة قاعدة البيانات: {e}")
    finally:
        if conn:
            conn.close()

def add_channel_to_db(channel_id, user_id):
    """إضافة قناة جديدة لقاعدة البيانات"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO channels (channel_id, user_id) VALUES (%s, %s) ON CONFLICT (channel_id) DO NOTHING", 
                   (str(channel_id), user_id))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"❌ خطأ عند إضافة القناة: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_user_channels(user_id):
    """جلب قائمة القنوات المرتبطة بمستخدم معين"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT channel_id FROM channels WHERE user_id = %s", (user_id,))
        channels = cur.fetchall()
        cur.close()
        return channels
    except Exception as e:
        print(f"❌ خطأ عند جلب القنوات: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_channel_from_db(channel_id):
    """حذف قناة من قاعدة البيانات (إلغاء الربط)"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM channels WHERE channel_id = %s", (str(channel_id),))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"❌ خطأ عند حذف القناة: {e}")
        return False
    finally:
        if conn:
            conn.close()

# تهيئة الجداول عند استيراد الملف
if DATABASE_URL:
    init_db()
    
