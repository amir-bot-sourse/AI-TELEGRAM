from flask import Flask
from threading import Thread
import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
logged_admins = set()
users = set()

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
    users.add(update.effective_user.id)

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
    await update.message.reply_text(
        f"👥 تعداد کاربران: {len(users)}"
    )

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in logged_admins:
        await update.message.reply_text(
            "🔒 اول /login رمز را وارد کن"
        )
        return

    await update.message.reply_text(
        "👑 پنل مدیریت\n\n"
        f"کاربران: {len(users)}"
    )

# ---------------- Chat ----------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users.add(update.effective_user.id)
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

# ---------------- Run ----------------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("login", login)) 

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
    web.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=run_web, daemon=True).start()

app.run_polling()
