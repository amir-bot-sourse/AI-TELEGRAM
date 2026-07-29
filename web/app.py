from flask import Flask, request
from telegram import Update
from bot import application
from config import BOT_TOKEN
import asyncio


app = Flask(__name__)


initialized = False


@app.route("/", methods=["GET"])
def home():
    return "AI Telegram Bot Running"


async def init_application():

    global initialized

    if not initialized:

        await application.initialize()
        initialized = True



@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():

    data = request.get_json()

    async def process():

        await init_application()

        update = Update.de_json(
            data,
            application.bot
        )

        await application.process_update(update)


    asyncio.run(process())

    return "OK"
