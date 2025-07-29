import logging
import core.config as config
from core.broker import AlpacaBroker, evaluate_and_place_order

# Setup logging
logging.basicConfig(level=logging.INFO)

# Instantiate broker
broker = AlpacaBroker(config)

# Test a symbol (e.g., TSLA)
symbol = "TSLA"
signal = 1  # Buy

print(f"Testing slippage logic with symbol: {symbol}")
price = broker.get_latest_price(symbol)
print(f"Latest price: ${price:.2f}" if price else "Price fetch failed.")

order = evaluate_and_place_order(broker, symbol, signal)

if order:
    print(f"✅ Order placed: {order}")
else:
    print(f"⛔ Order was skipped or failed.")
