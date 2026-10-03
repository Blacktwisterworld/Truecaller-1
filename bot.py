import os
import asyncio

from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from dataset import search_number


# =========================
# Flask Web Server
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Telegram Dataset Bot is running."


@app.route("/health")
def health():
    return "OK"


def run_web_server():
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================
# Telegram /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Bot Online\n\n"
        "Sirf number search karne ke liye:\n\n"
        "/search 6000010150"
    )


# =========================
# Telegram /search
# =========================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "❌ Number provide karo.\n\n"
            "Example:\n"
            "/search 6000010150"
        )

        return


    number = context.args[0].strip()


    if not number.isdigit():

        await update.message.reply_text(
            "❌ Sirf numeric number enter karo."
        )

        return


    # Initial message
    message = await update.message.reply_text(
        "🔍 Searching...\n\n"
        "📂 File 0/32"
    )


    # Current Telegram event loop
    loop = asyncio.get_running_loop()


    # Progress callback
    def progress_callback(text):

        future = asyncio.run_coroutine_threadsafe(
            message.edit_text(text),
            loop
        )

        try:
            future.result(timeout=10)

        except Exception as e:
            print(f"Progress update error: {e}")


    try:

        # Search ko separate thread me run karna
        # taaki Telegram bot block na ho
        result = await asyncio.to_thread(
            search_number,
            number,
            progress_callback
        )


        # =========================
        # MATCH FOUND
        # =========================

        if result:

            def clean(value):

                if value is None:
                    return "N/A"

                return str(value)


            response = (
                "✅ MATCH FOUND\n\n"

                f"🔢 Number: "
                f"{clean(result.get('Number'))}\n"

                f"👤 Name: "
                f"{clean(result.get('Name'))}\n"

                f"📍 Address: "
                f"{clean(result.get('Address'))}\n"

                f"📧 Email: "
                f"{clean(result.get('Email'))}\n"

                f"⚧ Gender: "
                f"{clean(result.get('Gender'))}\n"

                f"📡 Carrier: "
                f"{clean(result.get('Carrier'))}"
            )


        # =========================
        # NO MATCH
        # =========================

        else:

            response = (
                "❌ No match found\n\n"

                f"🔢 Number: {number}\n\n"

                "📂 32/32 files searched."
            )


        # Final result
        await message.edit_text(response)


    except Exception as e:

        print(f"Search error: {e}")

        await message.edit_text(
            "⚠️ Search ke waqt error aa gaya.\n\n"
            "Please try again."
        )


# =========================
# Telegram Bot
# =========================

async def run_bot():

    telegram_app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    telegram_app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    telegram_app.add_handler(
        CommandHandler(
            "search",
            search
        )
    )


    await telegram_app.initialize()

    await telegram_app.start()


    print("🤖 TELEGRAM BOT ONLINE")


    await telegram_app.updater.start_polling()


    # Bot ko continuously running rakho
    while True:

        await asyncio.sleep(3600)


# =========================
# Main
# =========================

def main():

    # Flask ko alag thread me run karo
    server_thread = Thread(
        target=run_web_server,
        daemon=True
    )

    server_thread.start()


    # Telegram bot
    asyncio.run(
        run_bot()
    )


# =========================
# Run
# =========================

if __name__ == "__main__":

    main()
