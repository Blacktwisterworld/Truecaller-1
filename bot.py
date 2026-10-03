import os
import asyncio

from flask import Flask
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
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
# Main Menu
# =========================

def main_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "🔎 Number Search",
                callback_data="number_search"
            )
        ],
        [
            InlineKeyboardButton(
                "👨‍💻 Developer About",
                callback_data="developer_about"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 <b>Welcome to Cyber Insight 309</b>\n\n"
        "👇 <b>Select an option:</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


# =========================
# Button Handler
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    # -------------------------
    # Number Search
    # -------------------------

    if query.data == "number_search":

        context.user_data["waiting_for_number"] = True

        await query.edit_message_text(
            "🔎 <b>Number Search</b>\n\n"
            "📱 Please send the number you want to search.\n\n"
            "Example:\n"
            "<code>6000010150</code>",
            parse_mode="HTML"
        )


    # -------------------------
    # Developer About
    # -------------------------

    elif query.data == "developer_about":

        await query.edit_message_text(
            "👨‍💻 <b>Developer About</b>\n\n"
            "⚡ <b>Cyber Insight 309</b>\n\n"
            "👨‍💻 Developer: Cyber Insight\n"
            "👤 Name: Devid\n"
            "📱 Telegram: @cyber_insight_309\n"
            "📸 Insta: cyber_insight_309\n\n"
            "🚀 Search Engine: DuckDB\n"
            "📂 Dataset Files: 32"
            + CREDIT,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="back_menu"
                    )
                ]
            ]),
            parse_mode="HTML"
        )


    # -------------------------
    # Back
    # -------------------------

    elif query.data == "back_menu":

        await query.edit_message_text(
            "🤖 <b>Welcome to Cyber Insight 309</b>\n\n"
            "👇 <b>Select an option:</b>",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )


# =========================
# Number Message
# =========================

async def number_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Check if bot is waiting for number
    if not context.user_data.get(
        "waiting_for_number"
    ):
        return


    number = update.message.text.strip()


    if not number.isdigit():

        await update.message.reply_text(
            "❌ <b>Sirf numeric number enter karo.</b>\n\n"
            "Example:\n"
            "<code>6000010150</code>",
            parse_mode="HTML"
        )

        return


    # Stop waiting
    context.user_data[
        "waiting_for_number"
    ] = False


    # Initial progress message
    message = await update.message.reply_text(
        "🔍 <b>Searching...</b>\n\n"
        "📂 File 0/32",
        parse_mode="HTML"
    )


    loop = asyncio.get_running_loop()


    # =========================
    # Progress Callback
    # =========================

    def progress_callback(text):

        future = asyncio.run_coroutine_threadsafe(
            message.edit_text(
                text,
                parse_mode="HTML"
            ),
            loop
        )

        try:

            future.result(
                timeout=10
            )

        except Exception as e:

            print(
                f"Progress update error: {e}"
            )


    try:

        result = await asyncio.to_thread(
            search_number,
            number,
            progress_callback
        )


        # =========================
        # MATCH FOUND
        # =========================

        if result and not result.get(
            "not_found"
        ):

            def clean(value):

                if value is None:
                    return "N/A"

                return str(value)


            matched_file = result.get(
                "matched_file"
            )

            matched_filename = result.get(
                "matched_filename"
            )

            search_time = result.get(
                "search_time",
                0
            )

            files_checked = result.get(
                "files_checked",
                matched_file
            )


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
                f"{clean(result.get('Carrier'))}\n\n"

                "━━━━━━━━━━━━━━━━━━\n"

                f"📂 <b>Matched File:</b> "
                f"{files_checked}/32\n"

                f"📄 <b>File:</b> "
                f"<code>{matched_filename}</code>\n"

                f"⏱️ <b>Search Time:</b> "
                f"{search_time:.2f} sec"

                + CREDIT
            )


        # =========================
        # NO MATCH
        # =========================

        else:

            search_time = 0

            if result:

                search_time = result.get(
                    "search_time",
                    0
                )


            response = (

                "❌ <b>NO MATCH FOUND</b>\n\n"

                f"🔢 <b>Number:</b> "
                f"{number}\n\n"

                "📂 <b>Files Checked:</b> "
                "32/32\n"

                f"⏱️ <b>Search Time:</b> "
                f"{search_time:.2f} sec"

                + CREDIT
            )


        await message.edit_text(
            response,
            parse_mode="HTML"
        )


    except Exception as e:

        print(
            f"Search error: {e}"
        )


        await message.edit_text(
            "⚠️ <b>Search ke waqt error aa gaya.</b>\n\n"
            "🔄 Please try again.",
            parse_mode="HTML"
        )


# =========================
# Run Telegram Bot
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
        CallbackQueryHandler(
            button_handler
        )
    )


    telegram_app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            number_message
        )
    )


    await telegram_app.initialize()

    await telegram_app.start()


    print(
        "🤖 TELEGRAM BOT ONLINE"
    )


    await telegram_app.updater.start_polling()


    while True:

        await asyncio.sleep(
            3600
        )


# =========================
# Main
# =========================

def main():

    server_thread = Thread(
        target=run_web_server,
        daemon=True
    )

    server_thread.start()


    asyncio.run(
        run_bot()
    )


# =========================
# Start
# =========================

if __name__ == "__main__":

    main()
