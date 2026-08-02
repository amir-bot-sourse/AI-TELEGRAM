from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN

from handlers.start import start
from handlers.chat import chat
from handlers.panel import panel
from handlers.callback import button_callback


application = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .build()
)


# شروع
application.add_handler(
    CommandHandler(
        "start",
        start
    )
)


# پنل
application.add_handler(
    CommandHandler(
        "panel",
        panel
    )
)


# دکمه های پنل
application.add_handler(
    CallbackQueryHandler(
        button_callback
    )
)


# پیام های معمولی AI
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)
