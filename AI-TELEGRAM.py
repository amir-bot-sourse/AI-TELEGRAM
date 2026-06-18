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

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی نداری")
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
        wait_msg = await update.message.reply_text(
            "⏳ درحال پردازش..."
        )

        answer = ask_ai(text)

        await wait_msg.edit_text(answer[:4000])

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

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)

print("🤖 Bot Started")

app.run_polling()
