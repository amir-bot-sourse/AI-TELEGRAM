import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8956812650:AAEqBvxxOeKOfAKS75joYUQLDjznI4mglw4"
OPENROUTER_API_KEY = "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"

ADMIN_ID = 8493963275

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
    return data["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات آنلاین است\n\n/help"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/help\n"
        "/panel\n"
        "/ping"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong")

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی نداری")
        return

    await update.message.reply_text(
        "👑 پنل مدیریت\n"
        "ربات فعال است"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text

        msg = await update.message.reply_text("⏳ درحال فکر کردن...")

        answer = ask_ai(text)

        await msg.edit_text(answer[:4000])

    except Exception as e:
        await update.message.reply_text(f"خطا:\n{e}")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("panel", panel))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)

print("🤖 Bot Started")
app.run_polling()
