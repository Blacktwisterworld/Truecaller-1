# Truecaller Telegram Bot

Telegram bot jo number se teeno parquet files mein search karta hai.

## Files Check Ki Jaati Hain
- combined_selected_columns.parquet (80 MB)
- combined_truecaller_data.parquet (2.27 GB)
- final_combined_data.parquet (72 MB)

## Deploy on Koyeb (Free, No Card)
1. GitHub pe push karo
2. Koyeb → Create Service → GitHub → select repo
3. Builder: Dockerfile
4. Instance: Nano (free)
5. Env var: BOT_TOKEN=<your_token>
6. Deploy

## Local Run
```bash
pip install -r requirements.txt
export BOT_TOKEN=your_token_here
python bot.py
