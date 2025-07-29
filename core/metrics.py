from prometheus_client import Gauge, start_http_server
import threading

# ─── Prometheus Metrics ─────────────────────────────────────────────────────────

equity_gauge = Gauge("bot_portfolio_equity", "Total account equity")
cash_gauge = Gauge("bot_portfolio_cash", "Total available cash")
position_gauge = Gauge("bot_position_value", "Value of individual positions", ["symbol"])
position_qty_gauge = Gauge("bot_position_qty", "Quantity of held positions", ["symbol"])

def setup_metrics(port=8001):
    # Run Prometheus HTTP server in a background thread
    threading.Thread(target=start_http_server, args=(port,), daemon=True).start()

def update_metrics(equity, cash, positions):
    equity_gauge.set(equity)
    cash_gauge.set(cash)

    # Clear old label values
    position_gauge.clear()
    position_qty_gauge.clear()

    for pos in positions:
        symbol = pos["symbol"]
        market_value = float(pos["market_value"])
        qty = float(pos["qty"])
        position_gauge.labels(symbol=symbol).set(market_value)
        position_qty_gauge.labels(symbol=symbol).set(qty)
