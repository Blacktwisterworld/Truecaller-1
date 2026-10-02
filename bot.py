import os
import time
import logging
import threading
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler

import duckdb
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", 8080))

HF_BASE = "https://huggingface.co/datasets/Cyber-insight-309/truecallerdata/resolve/main"

# Bina token — dataset public hai
FILES = [
    f"{HF_BASE}/combined_selected_columns.parquet",
    f"{HF_BASE}/combined_truecaller_data.parquet",
    f"{HF_BASE}/final_combined_data.parquet",
]

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("SET enable_http_metadata_cache=true;")
con.execute("SET enable_object_cache=true;")
con.execute("SET http_timeout=180000;")

cache = {}
CACHE_MAX = 1000
user_last = defaultdict(float)
RATE_LIMIT_SEC = 2


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"Health server running on port {PORT}")
    server.serve_forever()


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Truecaller Bot*\n\n"
        "Number bhejo, main teeno databases mein check karke details nikal dunga.\n\n"
        "⏳ Pehli query slow ho sakti hai (10-30 sec)\n"
        "Example: `9876543210`",
        parse_mode="Markdown",
    )


async def handle_number(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    now = time.time()
    if now - user_last[uid] < RATE_LIMIT_SEC:
        return
    user_last[uid] = now

    num = update.message.text.strip()

    if not num.isdigit() or not (5 <= len(num) <= 15):
        await update.message.reply_text("❌ Sirf valid number bhejo (5-15 digits).")
        return

    if num in cache:
        await update.message.reply_text(cache[num], parse_mode="Markdown")
        return

    wait_msg = await update.message.reply_text("⏳ Search kar raha hun teeno files mein...")
    await update.message.chat.send_action("typing")

    try:
        found_data = None
        found_source = None
        errors = []

        for i, url in enumerate(FILES, start=1):
            try:
                logger.info(f"Searching file {i}")
                query = f'SELECT * FROM read_parquet(\'{url}\') WHERE "Number" = ? LIMIT 1'
                result = con.execute(query, [num])
                cols = [d[0] for d in result.description]
                rows = result.fetchall()

                if rows:
                    found_data = (cols, rows[0])
                    found_source = url.split("/")[-1]
                    logger.info(f"Found in file {i}")
                    break
            except Exception as e:
                logger.warning(f"File {i} error: {e}")
                errors.append(str(e)[:80])
                continue

        try:
            await wait_msg.delete()
        except:
            pass

        if not found_data:
            msg = f"❌ `{num}` ka koi record nahi mila teeno files mein."
            if errors:
                msg += f"\n\n⚠️ {len(errors)} file(s) mein error aaya."
            cache[num] = msg
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        cols, row = found_data
        lines = [f"📋 *Record for {num}*", f"_Source: {found_source}_\n"]
        for c, v in zip(cols, row):
            val = "N/A" if v is None else str(v)
            lines.append(f"*{c}*: `{val}`")

        msg = "\n".join(lines)
        if len(msg) > 4000:
            msg = msg[:4000] + "\n... (truncated)"

        if len(cache) < CACHE_MAX:
            cache[num] = msg

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        logger.exception("Query failed")
        try:
            await wait_msg.delete()
        except:
            pass
        await update.message.reply_text(f"⚠️ Error: `{str(e)[:150]}`", parse_mode="Markdown")


def main():
    threading.Thread(target=start_health_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    logger.info("Bot starting (polling mode)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
