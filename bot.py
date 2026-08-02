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
from handlers.panel import panel, panel_button


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
        panel_button
    )
)


# پیام های معمولی
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)
