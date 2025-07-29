# monitoring/telegram_utils.py

import os
import requests
import logging
import re

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")


def strip_emojis(text):
    emoji_pattern = re.compile("[\U00010000-\U0010FFFF]", flags=re.UNICODE)
    return emoji_pattern.sub(r"", text)


def send_telegram_alert(message):
    if not token or not chat_id:
        logging.warning("Telegram credentials not set. Skipping alert.")
        return

    clean_message = strip_emojis(message)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": clean_message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Telegram alert sent.")
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")
