import telebot
from telebot import types
import config
from database import add_channel_to_db, get_user_channels, delete_channel_from_db

bot = telebot.TeleBot(config.BOT_TOKEN)

# --- الكيبورد الرئيسي ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📢 إدارة القنوات", callback_data="manage_channels")
    btn2 = types.InlineKeyboardButton("📝 نشر جديد", callback_data="new_post")
    btn3 = types.InlineKeyboardButton("👤 المطور", callback_data="owner_info")
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"👋 أهلاً بك في بوت إدارة القنوات المطور.", 
                     reply_markup=main_markup(), parse_mode="Markdown")

# --- معالجة الضغط على الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "manage_channels":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة قناة", callback_data="add_instruction"))
        markup.add(types.InlineKeyboardButton("❌ حذف قناة مرتبطة", callback_data="list_for_delete"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("📢 قسم إدارة القنوات\nاختر إجراءً مما يلي:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "add_instruction":
        bot.edit_message_text("ℹ️ لإضافة قناة جديدة:\n\n1. قم بإضافة البوت كمشرف في القناة.\n2. أرسل معرف القناة (ID) يبدأ بـ -100 هنا في المحادثة.", 
                              chat_id, message_id, reply_markup=main_markup())

    elif call.data == "list_for_delete":
        channels = get_user_channels(call.from_user.id)
        if not channels:
            bot.answer_callback_query(call.id, "⚠️ لا توجد قنوات مرتبطة حالياً.", show_alert=True)
            return

        markup = types.InlineKeyboardMarkup()
        for (ch_id,) in channels:
            markup.add(types.InlineKeyboardButton(f"🗑 حذف: {ch_id}", callback_data=f"del_{ch_id}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_channels"))
        bot.edit_message_text("اختر القناة التي تريد إلغاء ربطها:", chat_id, message_id, reply_markup=markup)

    elif call.data.startswith("del_"):
        target_id = call.data.replace("del_", "")
        if delete_channel_from_db(target_id):
            bot.answer_callback_query(call.id, "✅ تم إلغاء ربط القناة بنجاح.")
            handle_query(type('obj', (object,), {'data': 'list_for_delete', 'message': call.message, 'from_user': call.from_user, 'id': call.id}))
        else:
            bot.answer_callback_query(call.id, "❌ حدث خطأ أثناء الحذف.")

    elif call.data == "back_home":
        bot.edit_message_text("القائمة الرئيسية:", chat_id, message_id, reply_markup=main_markup())

# --- دالة استقبال معرف القناة (إضافة) ---
@bot.message_handler(func=lambda message: message.text.startswith("-100"))
def handle_add_channel(message):
    # حماية: المطور فقط من يضيف قنوات
    if message.from_user.id != config.OWNER_ID:
        return

    channel_id = message.text.strip()
    if add_channel_to_db(channel_id, message.from_user.id):
        bot.reply_to(message, f"✅ تم الربط بنجاح!\nالقناة {channel_id} أصبحت الآن في قاعدة بيانات PostgreSQL.", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ فشل الربط. قد تكون القناة مضافة بالفعل أو هناك مشكلة في PostgreSQL.")

bot.infinity_polling()
