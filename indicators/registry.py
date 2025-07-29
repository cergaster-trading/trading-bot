# indicators/registry.py

from . import (
    ema_crossover,
    rsi,
    macd,
    bollinger,
    supertrend,
    adx_di,
    stochastic,
    sma_rsi,
)

# Optional debug:
if __name__ == "__main__":
    from indicators.strategy_base import StrategyFactory
    print("Registered strategies:")
    for name in StrategyFactory._registry:
        print(" -", name)
