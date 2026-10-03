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
# Credit
# =========================

CREDIT = (
    "\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "⚡ Powered by Cyber Insight 309\n"
    "👨‍💻 Developer: Cyber Insight\n"
    "👤 Name: Devid\n"
    "📱 Telegram: @cyber_insight_309\n"
    "📸 Insta: cyber_insight_309\n"
    "━━━━━━━━━━━━━━━━━━"
)


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 <b>Bot Online</b>\n\n"
        "🔎 Sirf number search karne ke liye:\n\n"
        "📌 <code>/search 6000010150</code>",
        parse_mode="HTML"
    )


# =========================
# /search
# =========================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "❌ <b>Number provide karo.</b>\n\n"
            "📝 Example:\n"
            "<code>/search 6000010150</code>",
            parse_mode="HTML"
        )

        return


    number = context.args[0].strip()


    if not number.isdigit():

        await update.message.reply_text(
            "❌ <b>Sirf numeric number enter karo.</b>",
            parse_mode="HTML"
        )

        return


    # Initial message
    message = await update.message.reply_text(
        "🔍 <b>Searching...</b>\n\n"
        "📂 File 0/32",
        parse_mode="HTML"
    )


    # Current event loop
    loop = asyncio.get_running_loop()


    # Progress callback
    def progress_callback(text):

        future = asyncio.run_coroutine_threadsafe(
            message.edit_text(
                text,
                parse_mode="HTML"
            ),
            loop
        )

        try:
            future.result(timeout=10)

        except Exception as e:
            print(f"Progress update error: {e}")


    try:

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
                "✅ <b>MATCH FOUND</b>\n\n"

                f"🔢 <b>Number:</b> "
                f"{clean(result.get('Number'))}\n"

                f"👤 <b>Name:</b> "
                f"{clean(result.get('Name'))}\n"

                f"📍 <b>Address:</b> "
                f"{clean(result.get('Address'))}\n"

                f"📧 <b>Email:</b> "
                f"{clean(result.get('Email'))}\n"

                f"⚧ <b>Gender:</b> "
                f"{clean(result.get('Gender'))}\n"

                f"📡 <b>Carrier:</b> "
                f"{clean(result.get('Carrier'))}"

                + CREDIT
            )


        # =========================
        # NO MATCH
        # =========================

        else:

            response = (
                "❌ <b>NO MATCH FOUND</b>\n\n"

                f"🔢 <b>Number:</b> {number}\n\n"

                "📂 <b>32/32 files searched.</b>"

                + CREDIT
            )


        # Final result
        await message.edit_text(
            response,
            parse_mode="HTML"
        )


    except Exception as e:

        print(f"Search error: {e}")

        await message.edit_text(
            "⚠️ <b>Search ke waqt error aa gaya.</b>\n\n"
            "🔄 Please try again.",
            parse_mode="HTML"
        )


# =========================
# Start Bot
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


    # Bot continuously running
    while True:

        await asyncio.sleep(3600)


# =========================
# Main
# =========================

def main():

    # Flask server
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
