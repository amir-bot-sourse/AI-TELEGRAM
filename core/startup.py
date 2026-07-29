import logging

from services.memory_service import init_memory


def startup():

    logging.info("Starting AI Telegram Pro")

    # ساخت دیتابیس حافظه
    init_memory()

    logging.info("Memory system loaded")

    print("🚀 AI Telegram Pro Startup Complete")
