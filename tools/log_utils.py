import csv
import os
from datetime import datetime

LOG_FILE = "stop_loss_log.csv"

def log_stop_loss(symbol, qty, stop_price, limit_price):
    is_new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(["timestamp", "symbol", "qty", "stop_price", "limit_price"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            qty,
            stop_price,
            limit_price
        ])
