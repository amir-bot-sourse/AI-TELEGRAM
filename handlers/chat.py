from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from services.ai_service import ask_ai

from database import (
    update_activity,
    increase_messages,
    save_memory
)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return


    user_id = update.effective_user.id

    message = update.message.text


    update_activity(user_id)

    increase_messages(user_id)


    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )


    answer = ask_ai(message)


    save_memory(
        user_id,
        message,
        answer
    )


    await update.message.reply_text(
        answer
    )
