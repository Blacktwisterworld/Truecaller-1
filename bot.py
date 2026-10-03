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


# -------------------------
# Flask Web Server
# -------------------------

app = Flask(__name__)


@app.route("/")
def home():
    return "Telegram Dataset Bot is running."


@app.route("/health")
def health():
    return "OK"


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# -------------------------
# Telegram Commands
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Online\n\n"
        "Number search karne ke liye:\n\n"
        "/search 6000010150"
    )


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

    message = await update.message.reply_text(
        "🔍 Searching...\n\n"
        "📂 File 0/32"
    )

    loop = asyncio.get_running_loop()

    async def update_progress(text):
        try:
            await message.edit_text(text)
        except Exception as e:
            print(f"Progress update error: {e}")

    def progress_callback(text):
        asyncio.run_coroutine_threadsafe(
            update_progress(text),
            loop
        )

    try:

        result = await asyncio.to_thread(
            search_number,
            number,
            progress_callback
        )

        if result:

            def clean(value):
                return "N/A" if value is None else str(value)

            response = (
                "✅ MATCH FOUND\n\n"
                f"🔢 Number: {clean(result['Number'])}\n"
                f"👤 Name: {clean(result['Name'])}\n"
                f"📍 Address: {clean(result['Address'])}\n"
                f"📧 Email: {clean(result['Email'])}\n"
                f"⚧ Gender: {clean(result['Gender'])}\n"
                f"📡 Carrier: {clean(result['Carrier'])}"
            )

        else:

            response = (
                "❌ No match found\n\n"
                f"🔢 Number: {number}\n\n"
                "📂 32/32 files searched."
            )

        await message.edit_text(response)

    except Exception as e:

        print(f"Search error: {e}")

        await message.edit_text(
            "⚠️ Search ke waqt error aa gaya."
        )


# -------------------------
# Start Bot
# -------------------------

async def run_bot():

    telegram_app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    telegram_app.add_handler(
        CommandHandler("start", start)
    )

    telegram_app.add_handler(
        CommandHandler("search", search)
    )

    await telegram_app.initialize()
    await telegram_app.start()

    print("🤖 TELEGRAM BOT ONLINE")

    await telegram_app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


def main():

    server_thread = Thread(
        target=run_web_server,
        daemon=True
    )

    server_thread.start()

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
