from flask import Flask, request
from telegram import Update

from bot import application


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "AI Telegram Bot Running"


@app.route("/webhook", methods=["POST"])
async def webhook():

    data = request.get_json()

    update = Update.de_json(
        data,
        application.bot
    )

    await application.process_update(update)

    return "OK"
