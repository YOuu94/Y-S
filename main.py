import telebot
from telebot import types
import config
import database

bot = telebot.TeleBot(config.BOT_TOKEN)

# نصوص اللغتين
STRINGS = {
    "en": {
        "start": (
            "**What can this bot do?**\n\n"
            f"@{config.SUPPORT_CHANNEL_USER} is an awesome bot for channel owners that helps you "
            "to create rich posts, view stats and more.\n\n"
            "**Features:**\n"
            "• scheduled posts\n"
            "• reactions and inline-keyboards\n"
            "• subscribers stats\n"
            "• multiple admins\n"
            "• full version for free\n\n"
            "This bot is used in more than 500,000 channels.\n\n"
            f"Updates: @{config.SUPPORT_CHANNEL_USER}\n"
            "controller.bot"
        ),
        "add_ch": "**Add Channel**\n\nFollow these steps:\n1. Add @{bot_user} as admin.\n2. Forward a message here.",
        "settings": "Choose what to change:",
        "success_lang": "Language set to English! 🇺🇸"
    },
    "ar": {
        "start": (
            "**ماذا يمكن لهذا البوت أن يفعل؟**\n\n"
            f"@{config.SUPPORT_CHANNEL_USER} هو بوت رائع لأصحاب القنوات يساعدك "
            "على إنشاء منشورات احترافية، عرض الإحصائيات وأكثر.\n\n"
            "**المميزات:**\n"
            "• منشورات مجدولة\n"
            "• تفاعلات وأزرار شفافة\n"
            "• إحصائيات المشتركين\n"
            "• مدراء متعددون\n"
            "• نسخة مجانية بالكامل\n\n"
            "هذا البوت مستخدم في أكثر من 500,000 قناة.\n\n"
            f"تحديثات: @{config.SUPPORT_CHANNEL_USER}\n"
            "controller.bot"
        ),
        "add_ch": "**إضافة القناة**\n\nاتبع الخطوات:\n1. أضف @{bot_user} كمشرف.\n2. أرسل توجيهاً من القناة هنا.",
        "settings": "اختر ما تريد تغييره:",
        "success_lang": "تم ضبط اللغة إلى العربية! 🇸🇦"
    }
}

# ضبط قائمة الأوامر
bot.set_my_commands([
    types.BotCommand("newpost", "create a new post"),
    types.BotCommand("addchannel", "add a new channel"),
    types.BotCommand("mychannels", "edit your channels"),
    types.BotCommand("settings", "other settings"),
    types.BotCommand("lang", "change language"),
    types.BotCommand("help", "answers to basic questions")
])

@bot.message_handler(commands=['start'])
def start(message):
    lang = database.get_user_lang(message.from_user.id)
    bot.send_message(message.chat.id, STRINGS[lang]["start"], parse_mode="Markdown")

@bot.message_handler(commands=['addchannel'])
def add_ch_cmd(message):
    lang = database.get_user_lang(message.from_user.id)
    bot.send_message(message.chat.id, STRINGS[lang]["add_ch"].format(bot_user=config.BOT_USERNAME), parse_mode="Markdown")

@bot.message_handler(commands=['lang'])
def lang_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("English 🇺🇸", callback_data="set_en"),
               types.InlineKeyboardButton("العربية 🇸🇦", callback_data="set_ar"))
    bot.send_message(message.chat.id, "Select Language / اختر اللغة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def callback_lang(call):
    new_lang = call.data.split("_")[1]
    database.set_user_lang(call.from_user.id, new_lang)
    bot.answer_callback_query(call.id, STRINGS[new_lang]["success_lang"])
    bot.edit_message_text(STRINGS[new_lang]["start"], call.message.chat.id, call.message.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.forward_from_chat or (m.text and m.text.startswith("-100")))
def handle_ch(message):
    ch_id = message.forward_from_chat.id if message.forward_from_chat else message.text
    if database.add_channel_to_db(ch_id, message.from_user.id):
        bot.reply_to(message, "✅ Success / تم بنجاح")

bot.infinity_polling()
