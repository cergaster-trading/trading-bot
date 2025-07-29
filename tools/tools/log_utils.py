import csv
import os
from datetime import datetime

LOG_FILE = "stop_loss_log.csv"

def log_stop_loss(symbol, qty, stop_price, limit_price):
    headers = ["timestamp", "symbol", "qty", "stop_price", "limit_price"]
    data = [
        datetime.utcnow().isoformat(),
        symbol,
        qty,
        stop_price,
        limit_price
    ]

    write_header = not os.path.exists(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(headers)
        writer.writerow(data)
