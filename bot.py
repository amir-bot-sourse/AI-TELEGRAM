from telegram.ext import (
    Application,
    CommandHandler
)

from config import BOT_TOKEN

from handlers.start import start


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
