from telegram import Update
from telegram.ext import ContextTypes


async def button_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if query.data == "users":

        await query.edit_message_text(
            "👥 بخش کاربران فعال شد"
        )


    elif query.data == "stats":

        await query.edit_message_text(
            "📊 آمار ربات در حال آماده سازی..."
        )


    elif query.data == "memory":

        await query.edit_message_text(
            "🧠 سرویس حافظه فعال است"
        )
