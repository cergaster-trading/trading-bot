from prometheus_client import start_http_server, Gauge, Counter
import time
import threading

# ─── Metric Definitions ─────────────────────────────────────────────────────────

# Bot health and lifecycle
bot_uptime_seconds = Gauge(
    "bot_uptime_seconds",
    "Total uptime of the trading bot in seconds"
)

last_trade_timestamp = Gauge(
    "last_trade_timestamp",
    "UNIX timestamp of the last executed trade"
)

# Trade tracking
bot_trades_total = Counter(
    "bot_trades_total",
    "Number of trades submitted via strategy logic"
)

# Rebalancing process
rebalance_attempts_total = Counter(
    "rebalance_attempts_total",
    "Number of rebalance runs (successful or not)"
)

rebalance_successes_total = Counter(
    "rebalance_successes_total",
    "Number of successful rebalance runs"
)

rebalance_failures_total = Counter(
    "rebalance_failures_total",
    "Number of failed rebalance runs"
)

# Stop-loss tracking
stop_loss_orders_total = Counter(
    "stop_loss_orders_total",
    "Total number of stop-loss orders placed",
    ['symbol']
)

# ─── Uptime Tracker ─────────────────────────────────────────────────────────────

_start_time = time.time()

def _update_uptime():
    while True:
        bot_uptime_seconds.set(time.time() - _start_time)
        time.sleep(5)

# ─── Exporter Startup ───────────────────────────────────────────────────────────

def start_prometheus_server(port: int = 8001):
    start_http_server(port)
    threading.Thread(target=_update_uptime, daemon=True).start()
    print(f"✅ Prometheus metrics running on port {port}")
