from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from services.ai_service import ask_ai
from services.memory_service import (
    load_memory,
    save_memory
)

from database import (
    update_activity,
    increase_messages
)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id

    message = update.message.text

    # ثبت فعالیت
    update_activity(user_id)

    # افزایش تعداد پیام‌ها
    increase_messages(user_id)

    # حالت تایپ
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # بارگذاری حافظه
    history = load_memory(user_id)

    # گرفتن پاسخ AI
    answer = ask_ai(
        message,
        history
    )

    # ذخیره گفتگو
    save_memory(
        user_id,
        message,
        answer
    )

    # ارسال پاسخ
    await update.message.reply_text(answer)

    def update_activity(user_id):
    cursor.execute(
        """
        UPDATE users
        SET last_activity=CURRENT_TIMESTAMP
        WHERE user_id=?
        """,
        (user_id,)
    )
    conn.commit()


def increase_messages(user_id):
    cursor.execute(
        """
        UPDATE users
        SET message_count=message_count+1
        WHERE user_id=?
        """,
        (user_id,)
    )
    conn.commit()
