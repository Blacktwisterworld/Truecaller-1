import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

HF_DATASET = "Cyber-insight-309/Truecaller"
HF_REPO_TYPE = "dataset"
