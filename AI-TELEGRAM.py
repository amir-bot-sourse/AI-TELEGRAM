import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = "8956812650:AAEqBvxxOeKOfAKS75joYUQLDjznI4mglw4"
OPENROUTER_API_KEY = "MDk5NjYzODk1ODM6cXcxMzI5MTMyOQ=="

ADMIN_ID = 8493963275

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

users = set()
logged_admin = set()

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

        # جلوگیری از کرش
        if "choices" not in data:
            return f"❌ API ERROR:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ ERROR:\n{e}"


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text(
        "🤖 ربات روشن شد\n\n/start\n/help\n/login"
    )


# ================= HELP =================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/help\n/login username password\n/panel"
    )


# ================= LOGIN =================
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("❌ /login username password")
        return

    u, p = context.args

    if u == ADMIN_USER and p == ADMIN_PASS:
        logged_admin.add(update.effective_user.id)
        await update.message.reply_text("✅ وارد پنل شدی")
    else:
        await update.message.reply_text("⛔ اشتباهه")


# ================= PANEL =================
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in logged_admin:
        await update.message.reply_text("⛔ اول لاگین کن")
        return

    await update.message.reply_text(
        f"👑 پنل مدیریت\n\n👥 کاربران: {len(users)}"
    )


# ================= CHAT =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("/"):
        return

    users.add(update.effective_user.id)

    msg = await update.message.reply_text("⏳ درحال فکر کردن...")

    answer = ask_ai(text)

    await msg.edit_text(answer[:4000])


# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("panel", panel))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🤖 Bot Started")
app.run_polling()
