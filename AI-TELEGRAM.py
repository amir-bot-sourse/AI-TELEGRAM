import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================
BOT_TOKEN = "8956812650:AAEqBvxxOeKOfAKS75joYUQLDjznI4mglw4"
OPENROUTER_API_KEY = "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"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

users = set()

# ================== AI ==================
def ask_ai(text):
    try:
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

    except Exception as e:
        return f"❌ خطای AI: {e}"


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)

    await update.message.reply_text(
        "🤖 ربات روشن است\n"
        "پیام بده تا جواب بدم\n\n"
        "/help"
    )


# ================== HELP ==================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 دستورات:\n"
        "/start\n"
        "/help\n"
        "/stats\n"
        "/panel admin password"
    )


# ================== STATS ==================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👥 تعداد کاربران: {len(users)}"
    )


# ================== PANEL LOGIN ==================
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "logged" not in context.user_data:
        context.user_data["logged"] = False

    if not context.user_data["logged"]:

        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "🔐 ورود به پنل:\n"
                "/panel username password"
            )
            return

        username = context.args[0]
        password = context.args[1]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            context.user_data["logged"] = True
            await update.message.reply_text("✅ ورود موفق شد\n👑 پنل باز شد")
        else:
            await update.message.reply_text("⛔ نام کاربری یا رمز اشتباه است")
        return

    await update.message.reply_text(
        "👑 پنل مدیریت\n"
        f"👥 کاربران: {len(users)}"
    )


# ================== CHAT ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users.add(update.effective_user.id)

    text = update.message.text

    if text.startswith("/"):
        return

    wait = await update.message.reply_text("⏳ درحال پردازش...")

    answer = ask_ai(text)

    await wait.edit_text(answer[:4000])


# ================== RUN ==================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("panel", panel))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot Started")
app.run_polling()
