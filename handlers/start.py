from telegram import Update
from telegram.ext import ContextTypes

from database import save_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    save_user(user.id, user.first_name, user.username)

    await update.message.reply_text(
        "🤖 سلام {}\n\n"
        "من ربات هوش مصنوعی حرفه‌ای هستم.\n\n"
        "برای شروع پیام خود را ارسال کن.".format(
            user.first_name
        )
    )
