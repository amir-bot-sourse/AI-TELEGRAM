from telegram.ext import Application

from config import BOT_TOKEN

from handlers.start import start
from handlers.chat import chat

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters
)


application = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .build()
)


application.add_handler(
    CommandHandler(
        "start",
        start
    )
)


application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)
