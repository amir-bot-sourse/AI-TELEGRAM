from flask import Flask, request
from telegram import Update

import asyncio

from config import BOT_TOKEN
from bot import application


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "AI Telegram Bot Running"


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():

    data = request.get_json()

    update = Update.de_json(
        data,
        application.bot
    )

    asyncio.run(
        application.process_update(update)
    )

    return "OK"
