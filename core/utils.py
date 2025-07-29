from datetime import datetime, time
import pytz

from indicators.macd import MACDStrategy
from indicators.rsi import RSIStrategy
from indicators.bollinger import BollingerStrategy
from indicators.ema_crossover import EMACrossoverStrategy
from indicators.adx_di import ADXDIStrategy
from indicators.supertrend import SupertrendStrategy
from indicators.stochastic import StochasticStrategy

def is_market_open():
    """Check if US markets are open (Monday–Friday, 9:30 AM–4:00 PM ET)."""
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)

    market_open = time(9, 30)
    market_close = time(16, 0)

    is_weekday = now.weekday() < 5
    is_during_hours = market_open <= now.time() < market_close

    return is_weekday and is_during_hours

def get_strategy_instance(name, params):
    """Return an initialized strategy instance given its name and parameters."""
    strategy_map = {
        "macd": MACDStrategy,
        "rsi": RSIStrategy,
        "bollinger": BollingerStrategy,
        "ema_crossover": EMACrossoverStrategy,
        "adx_di": ADXDIStrategy,
        "supertrend": SupertrendStrategy,
        "stochastic": StochasticStrategy,
    }
    strategy_class = strategy_map.get(name)
    return strategy_class(params) if strategy_class else None
