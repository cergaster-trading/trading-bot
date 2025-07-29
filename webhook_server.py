# webhook_server.py
import os
from flask import Flask, request, abort
from datetime import datetime
import pytz
import json

# — your existing helpers from trading_bot.py — 
from trading_bot import send_telegram  # assumes trading_bot.py is in same folder

app = Flask(__name__)

# Optional: lock to Eastern time for your timestamps
EASTERN = pytz.timezone('US/Eastern')

# (Optional) Verify Alpaca webhook secret: set WEBHOOK_SECRET in your env
WEBHOOK_SECRET = os.getenv("ALPACA_WEBHOOK_SECRET", None)

@app.route("/webhook", methods=["POST"])
def alpaca_webhook():
    # 1) (Optional) verify signature header
    if WEBHOOK_SECRET:
        sig = request.headers.get("X-Alpaca-Signature", "")
        body = request.get_data(as_text=True)
        import hmac, hashlib
        mac = hmac.new(WEBHOOK_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, sig):
            abort(400, "Invalid signature")

    # 2) parse JSON payload
    payload = request.json or {}
    event = payload.get("event", "")
    data  = payload.get("data", {})

    # 3) only handle fills
    if event == "order_filled":
        oid    = data.get("id")
        sym    = data.get("symbol")
        side   = data.get("side")
        qty    = data.get("filled_qty")
        price  = data.get("filled_avg_price")
        tstamp = data.get("filled_at")

        # format a message
        ts_local = datetime.now(EASTERN).strftime("%Y-%m-%d %I:%M:%S %p ET")
        msg = (
            f"✅ [Webhook] Order filled: {side.upper()} {sym} {qty}@{float(price):.2f}\n"
            f"Order ID: {oid}\n"
            f"At (exchange): {tstamp}\n"
            f"Received: {ts_local}"
        )
        print(msg)
        send_telegram(msg)

    return ("", 204)

if __name__ == "__main__":
    # pick up FLASK_PORT or default to 5000
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
