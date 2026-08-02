from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN

from handlers.start import start
from handlers.chat import chat
from handlers.panel import panel


application = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .build()
)


# /start
application.add_handler(
    CommandHandler(
        "start",
        start
    )
)

# /panel
application.add_handler(
    CommandHandler(
        "panel",
        panel
    )
)

# پیام‌های معمولی
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)
