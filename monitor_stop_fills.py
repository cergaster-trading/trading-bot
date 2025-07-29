import logging
import csv
import os
from datetime import datetime, timedelta
from core.config import API_KEY, API_SECRET, BASE_URL
from alpaca_trade_api.rest import REST
from monitoring.telegram_utils import send_telegram_message as send_telegram
from datetime import timezone

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor_stop_fills")
api = REST(API_KEY, API_SECRET, BASE_URL)
LOG_FILE = "stop_fills_log.csv"

def log_stop_fill(symbol, qty, filled_price):
    headers = ["timestamp", "symbol", "qty", "filled_price"]
    data = [datetime.utcnow().isoformat(), symbol, qty, filled_price]
    write_header = not os.path.exists(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(headers)
        writer.writerow(data)

def monitor_stop_fills():
    logger.info("🚦 Checking for filled stop-loss orders...")
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        filled_orders = api.list_orders(status='filled', after=since_str)
        for order in filled_orders:
            if order.side == 'sell' and order.type == 'stop_limit':
                msg = f"🚨 {order.symbol}: Stop-loss was TRIGGERED at ${order.filled_avg_price}"
                logger.warning(msg)
                send_telegram(msg)
                log_stop_fill(order.symbol, order.qty, order.filled_avg_price)
    except Exception as e:
        logger.error(f"❌ Error checking stop-loss fills: {e}")
        send_telegram(f"❌ Failed to check stop-loss fills: {e}")

if __name__ == "__main__":
    monitor_stop_fills()
