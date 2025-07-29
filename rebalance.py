# rebalance.py

import logging
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

from core.config import API_KEY, API_SECRET, TARGET_WEIGHTS, SYMBOLS
from monitoring.prometheus_metrics import METRIC_TRADES
from monitoring.telegram_utils import send_telegram_message as send_telegram
from atr_filter_utils import apply_atr_regime

# ─── Setup Logging ──────────────────────────────────────────────────────────────
logger = logging.getLogger("rebalance")
logger.setLevel(logging.INFO)

# ─── Clients ─────────────────────────────────────────────────────────────────────
trading_client = TradingClient(API_KEY, API_SECRET)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# ─── ATR Regime Filter ──────────────────────────────────────────────────────────
def get_current_regime(symbol: str) -> int:
    try:
        df = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
        df.dropna(inplace=True)
        regimes, _ = apply_atr_regime(df)
        return regimes.iloc[-1]
    except Exception as e:
        logger.warning(f"⚠️ Failed to compute ATR regime for {symbol}: {e}")
        return 0  # Neutral by default

# ─── Rebalance Logic ─────────────────────────────────────────────────────────────
def rebalance():
    try:
        account = trading_client.get_account()
        cash = float(account.cash)

        positions_raw = trading_client.get_all_positions()
        positions = {p.symbol: {"value": float(p.market_value), "qty": float(p.qty)} for p in positions_raw}
        total_equity = cash + sum(p["value"] for p in positions.values())

        desired_alloc = {sym: TARGET_WEIGHTS[sym] * total_equity for sym in TARGET_WEIGHTS}

        for symbol in SYMBOLS:
            # Check regime
            regime = get_current_regime(symbol)
            if regime == -1:
                logger.info(f"⏭️ Skipping {symbol}: ATR regime is conservative")
                continue

            current_val = positions.get(symbol, {}).get("value", 0.0)
            current_qty = positions.get(symbol, {}).get("qty", 0.0)
            target_val = desired_alloc[symbol]
            diff = target_val - current_val

            if abs(diff) / total_equity < 0.02:
                logger.info(f"🔍 {symbol} already close to target allocation")
                continue

            side = OrderSide.BUY if diff > 0 else OrderSide.SELL

            # Get current market price
            try:
                trade = data_client.get_stock_latest_trade(StockLatestTradeRequest(symbol=symbol))
                price = trade.price
            except Exception as price_err:
                logger.warning(f"⚠️ Failed to fetch latest price for {symbol}: {price_err}")
                continue

            limit_price = round(price * (1.005 if side == OrderSide.BUY else 0.995), 2)
            qty = int(abs(diff) / limit_price)

            if qty < 1:
                logger.info(f"⚠️ Skipping {symbol}: calculated qty is 0")
                continue

            if side == OrderSide.SELL and current_qty < qty:
                logger.warning(f"⚠️ Not enough shares to sell {qty} {symbol}, holding only {current_qty}")
                continue

            order = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY,
            )

            try:
                trading_client.submit_order(order)
                METRIC_TRADES.inc()
                logger.info(f"✅ {side.name} {qty} {symbol} @ ${limit_price}")
            except Exception as order_err:
                msg = f"❌ Order failed for {symbol}: {order_err}"
                logger.exception(msg)
                send_telegram(msg)

        send_telegram("✅ Rebalance completed successfully")

    except Exception as e:
        msg = f"❌ Rebalance error: {e}"
        logger.exception(msg)
        send_telegram(msg)

# ─── Entry Point ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rebalance()
