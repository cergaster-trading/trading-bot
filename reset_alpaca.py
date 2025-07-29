import logging
from alpaca_trade_api.rest import REST, APIError
import core.config as config

logger = logging.getLogger("reset_alpaca")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def reset_paper_account():
    api = REST(config.API_KEY, config.API_SECRET, config.BASE_URL)

    try:
        # Cancel all open orders
        open_orders = api.list_orders(status="open")
        for order in open_orders:
            api.cancel_order(order.id)
        logger.info(f"🧹 Canceled {len(open_orders)} open orders")

        # Liquidate all positions
        positions = api.list_positions()
        for pos in positions:
            side = "sell" if float(pos.qty) > 0 else "buy"
            api.submit_order(
                symbol=pos.symbol,
                qty=abs(int(float(pos.qty))),
                side=side,
                type="market",
                time_in_force="day"
            )
        logger.info(f"💥 Liquidated {len(positions)} positions")

        # Log manual cash adjustment
        logger.info("🪙 Note: To simulate $17,500 starting capital, set STARTING_CAPITAL = 17500 in config.py")

    except APIError as e:
        logger.error(f"❌ Alpaca API error: {e}")
    except Exception as e:
        logger.error(f"❌ Reset failed: {e}")

if __name__ == "__main__":
    reset_paper_account()