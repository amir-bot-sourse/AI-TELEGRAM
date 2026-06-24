from flask import Flask
from threading import Thread
from telegram import Update
from flask import Flask,request
import asyncio
import traceback
import logging
import json
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
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS banned_users (
    user_id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

def is_banned(user_id):
    cursor.execute(
        "SELECT * FROM banned_users WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone() is not None
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

    if is_banned(update.effective_user.id):
        return

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

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    keyboard = [
    [InlineKeyboardButton("📊 آمار آنلاین", callback_data="stats")],
    [InlineKeyboardButton("👥 لیست کاربران", callback_data="users_list")],
    [InlineKeyboardButton("🚫 بن کاربر", callback_data="ban_menu")],
    [InlineKeyboardButton("📩 ارسال پیام", callback_data="sendto_menu")],
    [InlineKeyboardButton("💾 بکاپ دیتابیس", callback_data="backup")],
    [InlineKeyboardButton("⚙️ وضعیت ربات", callback_data="status")],
    [InlineKeyboardButton("🔄 ریست پنل", callback_data="reload")]
    ]

    await update.message.reply_text(
        f"👑 پنل PRO\n\n👥 کاربران: {users_count}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in logged_admins and user_id != ADMIN_ID:
        await query.edit_message_text("⛔ دسترسی نداری")
        return

    data = query.data

    # 📊 آمار
    if data == "stats":
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await query.edit_message_text(f"👥 تعداد کاربران: {count}")

    # 📢 راهنما ارسال
    elif data == "broadcast":
        await query.edit_message_text("📢 /broadcast متن پیام")

    # 🔄 ریست پنل
    elif data == "reload":
        await query.edit_message_text("🔄 پنل آپدیت شد")

    # 🚫 منوی بن
    elif data == "ban_menu":
        await query.edit_message_text("🚫 دستور: /ban user_id")

    # 📩 منوی send
    elif data == "sendto_menu":
        await query.edit_message_text("📩 دستور: /sendto user_id text")

    # 💾 بکاپ
    elif data == "backup":
        with open("users.db", "rb") as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=f,
                caption="💾 بکاپ دیتابیس"
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

    for user in users_list:
        try:
            await context.bot.send_message(
                chat_id=user[0],
                text=f"📢 پیام جدید:\n\n{text}"
            )
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ پایان ارسال\n\n"
        f"✔ موفق: {sent}\n"
        f"❌ ناموفق: {failed}"
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1:
        await update.message.reply_text("/ban user_id")
        return

    user_id = int(context.args[0])

    cursor.execute(
        "INSERT OR IGNORE INTO banned_users VALUES (?)",
        (user_id,)
    )
    conn.commit()

    await update.message.reply_text("🚫 بن شد")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1:
        await update.message.reply_text("/unban user_id")
        return

    user_id = int(context.args[0])

    cursor.execute(
        "DELETE FROM banned_users WHERE user_id=?",
        (user_id,)
    )
    conn.commit()

    await update.message.reply_text("✅ آنبن شد")

async def sendto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("/sendto user_id متن")
        return

    user_id = int(context.args[0])
    text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(user_id, text)
        await update.message.reply_text("✅ ارسال شد")

    except Exception as e:
        await update.message.reply_text(f"❌ خطا:\n{e}")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT user_id FROM users")

    txt = ""

    for user in cursor.fetchall():
        txt += str(user[0]) + "\n"

    await update.message.reply_text(txt[:4000])

import asyncio
import traceback
import logging

logger = logging.getLogger(__name__)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        save_user(user_id)
    except Exception:
        pass

    if is_banned(user_id):
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if not text:
        return

    try:
        answer = await asyncio.to_thread(ask_ai, text)

        if not answer:
            return

        await update.message.reply_text(answer[:4000])

    except Exception:
        logger.error(f"Error for user {user_id}:\n{traceback.format_exc()}")
        await update.message.reply_text("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
        # ---------------- Run ----------------
import asyncio
from flask import Flask, request
from telegram import Update

# =========================
# BOT APP
# =========================
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("sendto", sendto))
app.add_handler(CommandHandler("users", users_list))
app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)
print("🤖 Bot Started")

# =========================
# FLASK WEBHOOK SERVER
# =========================
web = Flask(__name__)
print("BOT_TOKEN =", BOT_TOKEN)
@web.route("/")
def home():
    return "HOME OK"

@web.route("/test")
def test():
    return "TEST OK"

@web.route(f"/{BOT_TOKEN}", methods=["GET", "POST"])
def webhook():
    return "WEBHOOK OK"
# =========================
# STARTUP WEBHOOK SETUP
# =========================
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print("TOKEN =", BOT_TOKEN)
async def setup():
    await app.initialize()

    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

    print("🔥 WEBHOOK SET OK")
    print("URL =", f"{WEBHOOK_URL}/{BOT_TOKEN}")

asyncio.run(setup())

print("🔥 WEBHOOK MODE STARTED")
# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)
