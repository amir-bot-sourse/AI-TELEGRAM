import asyncio
import traceback
import logging
import os
import requests
import sqlite3

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# LOGGING (FIXED)
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# ENV
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logged_admins = set()

# =========================
# DB
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY)")
conn.commit()


def save_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()


def is_banned(user_id):
    cursor.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None


# =========================
# AI
# =========================
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
        return "API ERROR"
    return data["choices"][0]["message"]["content"]


# =========================
# CHAT (FIXED PRO)
# =========================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    save_user(user_id)

    if is_banned(user_id):
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    try:
        answer = await asyncio.to_thread(ask_ai, text)
        await update.message.reply_text(answer[:4000])

    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text("❌ خطا")


# =========================
# BASIC COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text("🤖 Bot Online")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await update.message.reply_text(f"👥 Users: {count}")


# =========================
# PANEL PRO (حفظ شد)
# =========================
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="stats")],
        [InlineKeyboardButton("👥 کاربران", callback_data="users_list")],
        [InlineKeyboardButton("🚫 بن", callback_data="ban_menu")],
        [InlineKeyboardButton("📩 ارسال", callback_data="sendto_menu")],
        [InlineKeyboardButton("💾 بکاپ", callback_data="backup")],
        [InlineKeyboardButton("⚙️ وضعیت", callback_data="status")],
        [InlineKeyboardButton("🔄 ریست", callback_data="reload")]
    ]

    await update.message.reply_text(
        f"👑 PANEL PRO\n👥 Users: {users_count}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# CALLBACKS
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "stats":
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await query.edit_message_text(f"👥 {count}")

    elif data == "backup":
        with open("users.db", "rb") as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=f
            )

    elif data == "reload":
        await query.edit_message_text("🔄 Reloaded")

    elif data == "ban_menu":
        await query.edit_message_text("/ban user_id")

    elif data == "sendto_menu":
        await query.edit_message_text("/sendto user_id text")


# =========================
# BOT APP
# =========================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
)

print("🤖 BOT STARTED")


# =========================
# FLASK
# =========================
web = Flask(__name__)


@web.route("/")
def home():
    return "Bot Online"


@web.post(f"/{BOT_TOKEN}")
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, app.bot)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app.process_update(update))

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok", 200


# =========================
# STARTUP (FIXED)
# =========================
async def setup():
    await app.initialize()
    await app.start()

    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

    print("🔥 WEBHOOK SET OK")


asyncio.run(setup())

print("🔥 READY")


# =========================
# RUN
# =========================
web.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    use_reloader=False
        )
