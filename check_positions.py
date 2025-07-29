from alpaca.trading.client import TradingClient
from config import API_KEY, API_SECRET

client = TradingClient(API_KEY, API_SECRET)
positions = client.get_all_positions()

for p in positions:
    print(f"{p.symbol}: {p.qty} shares @ ${p.market_value}")
