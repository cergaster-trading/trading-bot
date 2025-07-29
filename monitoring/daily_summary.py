# monitoring/daily_summary.py
from datetime import timezone
import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
import logging
import csv
import os
from datetime import datetime
from core.config import API_KEY, API_SECRET, BASE_URL
from alpaca_trade_api.rest import REST
from monitoring.telegram_utils import send_telegram_message as send_telegram
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("daily_summary")
api = REST(API_KEY, API_SECRET, BASE_URL)
FILL_LOG = "stop_fills_log.csv"

# Email config (uses .env variables)
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
SMTP_USER = os.getenv("EMAIL_USERNAME")
SMTP_PASS = os.getenv("EMAIL_PASSWORD")


def summarize_fills():
    today = datetime.now(timezone.utc).date()
    realized = {}
    if not os.path.exists(FILL_LOG):
        return realized

    with open(FILL_LOG, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['timestamp'].startswith(str(today)):
                symbol = row['symbol']
                qty = float(row['qty'])
                price = float(row['filled_price'])
                realized[symbol] = realized.get(symbol, 0) + (qty * price * -1)  # sells are losses
    return realized


def summarize_positions():
    positions = api.list_positions()
    unrealized = {}
    snapshot = []
    for p in positions:
        symbol = p.symbol
        unrealized_pl = float(p.unrealized_pl)
        unrealized[symbol] = unrealized_pl
        snapshot.append(f"{symbol}: {p.qty} @ ${p.avg_entry_price} → ${p.current_price} ({unrealized_pl:+.2f})")
    return unrealized, snapshot


def format_message(realized, unrealized, snapshot):
    lines = ["*📊 Daily Summary*"]
    net_realized = sum(realized.values())
    net_unrealized = sum(unrealized.values())

    if realized:
        lines.append("\n*🔁 Realized P/L:*")
        for s, v in realized.items():
            lines.append(f"- {s}: ${v:.2f}")
    else:
        lines.append("\n🔁 No realized gains/losses today.")

    if unrealized:
        lines.append("\n*📈 Unrealized P/L:*")
        for s, v in unrealized.items():
            lines.append(f"- {s}: ${v:.2f}")

    lines.append("\n*📋 Current Positions:*")
    lines.extend(snapshot)

    lines.append(f"\n💵 *Net Realized:* ${net_realized:.2f}")
    lines.append(f"📦 *Net Unrealized:* ${net_unrealized:.2f}")

    return "\n".join(lines)


def send_email(subject, body):
    if not EMAIL_ENABLED:
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logger.info("✉️ Email summary sent")
    except Exception as e:
        logger.error(f"❌ Failed to send email summary: {e}")


def run_daily_summary():
    realized = summarize_fills()
    unrealized, snapshot = summarize_positions()
    message = format_message(realized, unrealized, snapshot)
    send_telegram(message)
    send_email("Daily Bot Summary", message)


if __name__ == "__main__":
    run_daily_summary()
