# core/broker.py

import alpaca_trade_api as tradeapi
import logging
from datetime import datetime
from monitoring.telegram_utils import send_telegram_alert


class AlpacaBroker:
    def __init__(self, config):
        self.api_key = config.ALPACA_API_KEY
        self.secret_key = config.ALPACA_SECRET_KEY
        self.base_url = config.ALPACA_BASE_URL
        self.api = tradeapi.REST(self.api_key, self.secret_key, self.base_url, api_version="v2")

        try:
            account = self.api.get_account()
            logging.info(f"🔐 Connected to Alpaca: {account.status} | Equity: ${account.equity}")
            logging.info(f"📛 Account ID: {account.id} | Buying Power: ${account.buying_power}")
        except Exception as e:
            logging.error(f"❌ Failed to connect to Alpaca: {e}")
            raise

    def get_cash(self):
        try:
            account = self.api.get_account()
            return float(account.cash)
        except Exception as e:
            logging.error(f"❌ Error getting cash balance: {e}")
            return 0.0

    def get_equity(self):
        try:
            account = self.api.get_account()
            return float(account.equity)
        except Exception as e:
            logging.error(f"❌ Error getting equity: {e}")
            return 0.0

    def get_position(self, symbol):
        try:
            position = self.api.get_position(symbol)
            return float(position.qty)
        except tradeapi.rest.APIError:
            return 0  # No position
        except Exception as e:
            logging.error(f"❌ Error fetching position for {symbol}: {e}")
            return 0

    def close_position(self, symbol):
        try:
            order = self.api.close_position(symbol)
            logging.info(f"✅ Closed position for {symbol}")
            return order
        except Exception as e:
            logging.error(f"❌ Error closing position for {symbol}: {e}")
            return None

    def get_latest_price(self, symbol):
        try:
            quote = self.api.get_latest_trade(symbol)
            return float(quote.price)
        except Exception as e:
            logging.error(f"❌ Error fetching latest price for {symbol}: {e}")
            return None

    def calculate_quantity(self, symbol, allocation_pct):
        try:
            cash = self.get_cash()
            alloc_cash = cash * allocation_pct
            price = self.get_latest_price(symbol)
            if not price or price == 0:
                logging.warning(f"⚠️ Skipping quantity calc for {symbol}: invalid price {price}")
                return 0
            qty = int(alloc_cash // price)
            return qty
        except Exception as e:
            logging.error(f"❌ Error calculating quantity for {symbol}: {e}")
            return 0

    def submit_order(self, symbol, qty, side, take_profit=None, stop_loss=None, reason=None):
        try:
            order_data = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": "market",
                "time_in_force": "gtc"
            }

            if take_profit or stop_loss:
                order_data["order_class"] = "bracket"
                if take_profit:
                    order_data["take_profit"] = {"limit_price": round(take_profit, 2)}
                if stop_loss:
                    order_data["stop_loss"] = {"stop_price": round(stop_loss, 2)}

            order = self.api.submit_order(**order_data)

            # Send Telegram alert
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            price = self.get_latest_price(symbol)
            message = f"""*🔔 Trade Executed*
----------------------------------------
🟦 *Symbol:* `{symbol}`
🛒 *Action:* `{side.upper()}`
📦 *Qty:* `{qty}`
💵 *Price:* `${price:.2f}`
📅 *Time:* `{now}`
🧠 *Reason:* `{reason or 'N/A'}`\n"""

            if stop_loss:
                message += f"🛑 *Stop-Loss:* `${stop_loss:.2f}`\n"
            if take_profit:
                message += f"🎯 *Take-Profit:* `${take_profit:.2f}`\n"

            send_telegram_alert(message)

            logging.info(f"✅ Order submitted: {symbol} | {side.upper()} | Qty: {qty} | TP: {take_profit} | SL: {stop_loss}")
            return order

        except Exception as e:
            logging.error(f"❌ Error submitting order for {symbol}: {e}")
            send_telegram_alert(f"❌ *Order failed for {symbol}*: `{e}`")
            return None

    def cancel_all_orders(self):
        try:
            self.api.cancel_all_orders()
            logging.info("🔁 All open orders cancelled.")
        except Exception as e:
            logging.error(f"❌ Error cancelling all orders: {e}")
