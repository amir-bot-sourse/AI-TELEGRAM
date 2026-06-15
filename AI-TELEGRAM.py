import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = "8956812650:AAEqBvxxOeKOfAKS75joYUQLDjznI4mglw4"
OPENROUTER_API_KEY = "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"
ADMIN_ID = 8493963275

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

users = set()
logged_admins = set()

# ================= AI =================
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
                    {"role": "system", "content": "تو یک دستیار فارسی هستی"},
                    {"role": "user", "content": text}
                ]
            },
            timeout=60
        )

        data = r.json()

        # 🛑 اگر API خطا داد
        if "choices" not in data:
            return f"❌ API Error:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Request Error: {e}"


# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text(
        "🤖 ربات روشن است\n/help برای راهنما"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/help\n/login username password\n/panel"
    )


# ================= LOGIN =================
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("❌ /login username password")
        return

    username, password = context.args

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        logged_admins.add(update.effective_user.id)
        await update.message.reply_text("✅ وارد پنل شدی")
    else:
        await update.message.reply_text("⛔ اطلاعات اشتباه")


# ================= PANEL =================
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in logged_admins:
        await update.message.reply_text("⛔ اول لاگین کن")
        return

    await update.message.reply_text(
        f"👑 پنل مدیریت\n\n👥 کاربران: {len(users)}"
    )


# ================= CHAT =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)

    text = update.message.text

    if text.startswith("/"):
        return

    wait = await update.message.reply_text("⏳ فکر میکنم...")

    answer = ask_ai(text)

    await wait.edit_text(answer[:4000])


# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("panel", panel))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot Started")
app.run_polling()
