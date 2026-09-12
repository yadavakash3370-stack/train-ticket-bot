import asyncio
import threading

from flask import Flask, jsonify
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, PORT
from bot.handlers import router


# ==========================================================
# FLASK SERVER
# ==========================================================

app = Flask(__name__)


@app.route("/")
def home():

    return jsonify({
        "status": "online",
        "service": "Train Ticket Telegram Bot",
        "mode": "dummy"
    })


@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


def run_flask():

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False,
    )


# ==========================================================
# TELEGRAM BOT
# ==========================================================

async def run_bot():

    bot = Bot(
        token=BOT_TOKEN
    )

    dp = Dispatcher()

    dp.include_router(router)

    print("Telegram bot starting...")

    try:

        await dp.start_polling(bot)

    finally:

        await bot.session.close()


# ==========================================================
# MAIN
# ==========================================================

def main():

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True,
    )

    flask_thread.start()

    print(
        f"Flask server started on port {PORT}"
    )

    asyncio.run(
        run_bot()
    )


if __name__ == "__main__":
    main()
