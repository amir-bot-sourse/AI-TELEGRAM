from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from services.ai_service import ask_ai
from database import (
    update_activity,
    increase_messages
)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id

    message = update.message.text


    # ثبت فعالیت کاربر
    update_activity(user_id)


    # افزایش تعداد پیام
    increase_messages(user_id)


    # حالت تایپ کردن
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )


    answer = ask_ai(message)


    await update.message.reply_text(
        answer
    )
