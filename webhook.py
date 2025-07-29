# webhook.py
from flask import Flask, request, abort
import os
import json
from datetime import datetime
import pytz

from trading_bot import send_telegram   # reuse your helper
import config

EASTERN = pytz.timezone('US/Eastern')

app = Flask(__name__)

# (Optional) verify this matches your Alpaca webhook signing secret
WEBHOOK_SECRET = os.environ.get("APCA_WEBHOOK_SECRET", "")

@app.route("/webhook", methods=["POST"])
def on_webhook():
    # 1) (Optional) verify signature
    # sig = request.headers.get("APCA-WEBHOOK-SECRET", "")
    # if sig != WEBHOOK_SECRET:
    #     abort(403)

    data = request.get_json(force=True)
    # we only care about trade_updates of type "fill"
    if data.get("stream") == "trade_updates":
        t = data["data"]
        if t.get("event") == "fill":
            filled = t["order"]
            ts = datetime.now(EASTERN).strftime("%Y-%m-%d %I:%M:%S %p ET")
            sym   = filled["symbol"]
            side  = filled["side"].upper()
            qty   = filled["filled_qty"]
            price = float(filled["filled_avg_price"])
            msg = (
                f"✅ FILLED {side} {sym} {qty}@{price:.2f}  ({ts})\n"
                f"Order ID: {filled['id']}"
            )
            print(msg)
            send_telegram(msg)
    return "", 200

if __name__ == "__main__":
    # By default listens on port 5000
    app.run(host="0.0.0.0", port=5000)
