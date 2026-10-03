# Telegram Dataset Bot

Telegram bot that searches a Hugging Face Parquet dataset
file-by-file without loading the complete dataset into RAM.

## Architecture

Telegram
↓
Render
↓
Hugging Face Dataset
↓
Parquet files searched sequentially

## Dataset

Repository:

Cyber-insight-309/Truecaller

Parquet files:

idx_phone.0.parquet
idx_phone.1.parquet
...
idx_phone.31.parquet

## Environment Variable

TELEGRAM_BOT_TOKEN

The Telegram bot token must be configured in Render
Environment Variables and must not be committed to GitHub.

## Run

```bash
pip install -r requirements.txt
python bot.py
