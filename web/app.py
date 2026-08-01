from flask import Flask, request
from telegram import Update
import asyncio
import threading

from bot import application


app = Flask(__name__)


loop = asyncio.new_event_loop()


def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


threading.Thread(
    target=start_loop,
    daemon=True
).start()



async def init_bot():

    await application.initialize()
    await application.start()


asyncio.run_coroutine_threadsafe(
    init_bot(),
    loop
)



@app.route("/")
def home():
    return "AI Telegram Bot Running"



@app.route("/webhook", methods=["POST"])
@app.route("/<token>", methods=["POST"])
def webhook(token=None):

    data = request.get_json(force=True)

    update = Update.de_json(
        data,
        application.bot
    )


    asyncio.run_coroutine_threadsafe(
        application.process_update(update),
        loop
    )


    return "OK"
