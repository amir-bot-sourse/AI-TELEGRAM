from flask import Flask
from threading import Thread
import os
import requests
import sqlite3
import sys
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

if "RENDER" in os.environ:
    import os
    os.environ["PYTHONUNBUFFERED"] = "1"

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
logged_admins = set()
users = set()
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

def save_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
# ---------------- AI ----------------
def ask_ai(text):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "تو یک دستیار فارسی حرفه‌ای هستی"},
                {"role": "user", "content": text}
            ]
        },
        timeout=60
    )

    data = r.json()

    if "choices" not in data:
        return f"❌ API ERROR:\n{data}"

    return data["choices"][0]["message"]["content"]

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ فقط ادمین")
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "استفاده:\n/login رمز"
        )
        return

    password = context.args[0]

    if password == ADMIN_PASSWORD:
        logged_admins.add(update.effective_user.id)
        await update.message.reply_text(
            "✅ ورود موفق"
        )
    else:
        await update.message.reply_text(
            "❌ رمز اشتباه"
        )

# ---------------- Commands ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    await update.message.reply_text(
        "🤖 سلام\n\n"
        "من ربات هوش مصنوعی هستم.\n\n"
        "/help"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 دستورات:\n\n"
        "/start\n"
        "/help\n"
        "/stats\n"
        "/panel"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    await update.message.reply_text(
        f"👥 تعداد کاربران: {count}"
    )


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in logged_admins and user_id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی نداری")
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    keyboard = [
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("🔄 Reload", callback_data="reload")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👑 پنل ادمین حرفه‌ای\n\n"
        f"👥 کاربران: {users_count}\n"
        f"⚡ وضعیت: آنلاین\n\n"
        "👇 یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in logged_admins and user_id != ADMIN_ID:
        await query.edit_message_text("⛔ دسترسی نداری")
        return

    data = query.data

    if data == "stats":
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await query.edit_message_text(f"👥 تعداد کاربران: {count}")

    elif data == "broadcast":
        await query.edit_message_text(
            "📢 برای ارسال پیام:\n/broadcast متن پیام"
        )

    elif data == "reload":
        await query.edit_message_text("🔄 پنل آپدیت شد")  
        
 
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    save_user(update.effective_user.id) 
    text = update.message.text

    try:
        from telegram.constants import ChatAction

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        answer = ask_ai(text)

        await update.message.reply_text(answer[:4000])

    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا:\n{e}"
        )
        async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if (
        update.effective_user.id not in logged_admins
        and update.effective_user.id != ADMIN_ID
    ):
        await update.message.reply_text("⛔ فقط ادمین")
        return

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "استفاده:\n/broadcast پیام"
        )
        return

    cursor.execute("SELECT user_id FROM users")
    users_list = cursor.fetchall()

    total = len(users_list)
    sent = 0
    failed = 0

    msg = await update.message.reply_text(
        f"📢 شروع ارسال...\n👥 تعداد: {total}"
    )

    for user in users_list:
        try:
            await context.bot.send_message(
                chat_id=user[0],
                text=f"📢 پیام جدید:\n\n{text}"
            )
            sent += 1

        except Exception:
            failed += 1

    await msg.edit_text(
        f"✅ پایان ارسال\n\n"
        f"👥 کل: {total}\n"
        f"✔ ارسال موفق: {sent}\n"
        f"❌ ناموفق: {failed}"
    )
# ---------------- Run ----------------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)
print("🤖 Bot Started")

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Online"

def run_web():
    print("🔥 FLASK STARTING...")
    web.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        use_reloader=False
    )

Thread(target=run_web, daemon=True).start()

print("🔥 THREAD STARTED")

app.run_polling(drop_pending_updates=True)
