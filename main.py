from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

from config import BOT_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام امیر 👋\n\nربات با موفقیت اجرا شد."
    )


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

print("🤖 Bot Started Successfully")

app.run_polling()
