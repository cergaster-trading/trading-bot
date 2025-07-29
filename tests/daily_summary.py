import os
import csv
import smtplib
import ssl
import json
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
import pandas as pd
import urllib.request
import urllib.parse

import config

EASTERN = pytz.timezone("US/Eastern")

def escape_md(text):
    return re.sub(r"([_*`\\[\\]()~>#+=|{}.!\\])", r"\\\\\\1", str(text))

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)

def send_email(subject, body):
    if not getattr(config, "EMAIL_ENABLED", False):
        return

    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_FROM
    msg["To"] = config.EMAIL_TO
    msg["Subject"] = subject

    plain_msg = re.sub(r"[*_`]", "", body)
    msg.attach(MIMEText(plain_msg, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP(config.EMAIL_SMTP_HOST, config.EMAIL_SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_FROM, config.EMAIL_TO, msg.as_string())

def run_daily_summary():
    ts = datetime.now(EASTERN).strftime("%Y-%m-%d")
    equity, cash, realized_pnl = 0, 0, 0
    positions = {}
    fills = []

    if os.path.exists("trade_log.csv"):
        with open("trade_log.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["timestamp"].startswith(ts):
                    fills.append(row)

    if os.path.exists("fills_log.csv"):
        df = pd.read_csv("fills_log.csv")
        df.columns = [col.strip().lower() for col in df.columns]
        if "fill_time" in df.columns:
            df["fill_time"] = pd.to_datetime(df["fill_time"], errors="coerce")
            today = datetime.now(EASTERN).date()
            df_today = df[df["fill_time"].dt.date == today]
            if "price" in df_today.columns and "qty" in df_today.columns:
                realized_pnl = (df_today["price"].astype(float) * df_today["qty"].astype(int)).sum()

    try:
        req = urllib.request.Request(
            config.BASE_URL + "/v2/account",
            headers={
                "APCA-API-KEY-ID": config.API_KEY,
                "APCA-API-SECRET-KEY": config.API_SECRET
            }
        )
        with urllib.request.urlopen(req) as r:
            acc_data = json.load(r)
            equity = float(acc_data["equity"])
            cash = float(acc_data["cash"])
    except Exception as e:
        print("Account API error:", e)

    msg = f"*Daily Summary — {ts}*\n\n"
    msg += f"*Equity:* \\${equity:,.2f}\n"
    msg += f"*Cash:* \\${cash:,.2f}\n"
    msg += f"*Realized P/L:* \\${realized_pnl:,.2f}\n\n"

    if fills:
        msg += "*Trades Executed:*\n"
        for fill in fills:
            msg += f"- {escape_md(fill['symbol'])} {fill['side']} {fill['qty']} @ \\${float(fill['price']):.2f}\n"
    else:
        msg += "_No trades today._\n"

    send_telegram(msg)
    send_email(subject=f"Daily P/L Summary ({ts})", body=msg)

if __name__ == "__main__":
    run_daily_summary()