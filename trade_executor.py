# trade_executor.py

import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from config import API_KEY, API_SECRET
from prometheus_metrics import METRIC_TRADES
import json

# Initialize logging
logger = logging.getLogger("trade_executor")
logger.setLevel(logging.INFO)

# Initialize Alpaca trading client
trading_client = TradingClient(API_KEY, API_SECRET)

# Load tuned parameters (including position_fraction per symbol)
try:
    with open("ensemble_tuned_params.json") as f:
        TUNED_PARAMS = json.load(f)
except Exception as e:
    logger.warning(f"⚠️ Could not load ensemble_tuned_params.json: {e}")
    TUNED_PARAMS = {}

def execute_trade(symbol, signal, df, cash, positions):
    """
    Execute a buy or sell trade for a given symbol based on the trading signal.
    Applies AI-tuned position sizing via ensemble_tuned_params.json.
    Logs all executions and updates Prometheus metrics.
    """
    price = df["close"].iloc[-1]
    params = TUNED_PARAMS.get(symbol, {})
    risk_fraction = params.get("position_fraction", 0.1)  # fallback to 10%

    # Buy logic
    if signal == "buy" and symbol not in positions:
        qty = int((cash * risk_fraction) / price)
        if qty <= 0:
            logger.warning(f"⚠️ Skipping buy for {symbol}: qty={qty}, cash={cash:.2f}, price={price:.2f}")
            return 0, 0

        try:
            order = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY,
            )
            trading_client.submit_order(order)
            METRIC_TRADES.inc()
            logger.info(f"🟢 BUY {qty} {symbol} @ ${price:.2f} (${qty * price:.2f})")
            return qty, qty * price
        except Exception as e:
            logger.error(f"❌ Failed to submit BUY for {symbol}: {e}")
            return 0, 0

    # Sell logic
    elif signal == "sell" and symbol in positions:
        qty = positions[symbol]
        if qty <= 0:
            logger.warning(f"⚠️ Skipping sell for {symbol}: position is 0")
            return 0, 0

        try:
            trading_client.close_position(symbol)
            METRIC_TRADES.inc()
            logger.info(f"🔴 SELL {qty} {symbol} @ ${price:.2f} (${qty * price:.2f})")
            return -qty, -qty * price
        except Exception as e:
            logger.error(f"❌ Failed to submit SELL for {symbol}: {e}")
            return 0, 0

    return 0, 0
