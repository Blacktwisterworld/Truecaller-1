import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from dataset import search_number


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Online\n\n"
        "Number search karne ke liye:\n"
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
            "❌ Sirf numeric value enter karo."
        )
        return

    message = await update.message.reply_text(
        "🔍 Searching...\n"
        "Please wait."
    )

    try:
        # Dataset search ko background thread mein run karenge
        result = await asyncio.to_thread(
            search_number,
            number
        )

        if result:
            def clean(value):
                return "N/A" if value is None else str(value)

            response = (
                "✅ Match Found\n\n"
                f"Number: {clean(result['Number'])}\n"
                f"Name: {clean(result['Name'])}\n"
                f"Address: {clean(result['Address'])}\n"
                f"Email: {clean(result['Email'])}\n"
                f"Gender: {clean(result['Gender'])}\n"
                f"Carrier: {clean(result['Carrier'])}"
            )
        else:
            response = (
                "❌ No match found.\n\n"
                f"Number: {number}"
            )

        await message.edit_text(response)

    except Exception as e:
        print(f"Search error: {e}")

        await message.edit_text(
            "⚠️ Search ke waqt error aa gaya.\n"
            "Please try again."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("search", search)
    )

    print("🤖 BOT ONLINE")

    app.run_polling()


if __name__ == "__main__":
    main()
