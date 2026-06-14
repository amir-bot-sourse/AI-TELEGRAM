import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8956812650:AAEqBvxxOeKOfAKS75joYUQLDjznI4mglw4"
OPENROUTER_API_KEY = "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"

# 🤖 AI
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
                {"role": "system", "content": "تو یک دستیار فارسی هستی"},
                {"role": "user", "content": text}
            ]
        }
    )
    return r.json()["choices"][0]["message"]["content"]

# 🚀 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ربات روشنه\nپیام بده")

# 🧠 فقط پیام عادی
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 🚫 دستورها رد شوند
    if text.startswith("/"):
        return

    try:
        answer = ask_ai(text)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(str(e))

# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

# ⚡ مهم: اول دستورها
app.add_handler(CommandHandler("start", start))

# ⚡ فقط پیام معمولی
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot Started")
app.run_polling()