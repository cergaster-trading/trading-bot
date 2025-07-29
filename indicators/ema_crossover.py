# indicators/ema_crossover.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class EMACrossoverStrategy(StrategyBase):
    def __init__(self, df, ema_crossover_fast_period=10, ema_crossover_slow_period=50):
        self.df = df.copy()
        self.fast = ema_crossover_fast_period
        self.slow = ema_crossover_slow_period
        self.name = "ema_crossover"

    def generate_signals(self):
        df = self.df.copy()
        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()

        df["signal"] = 0
        df.loc[df["ema_fast"] > df["ema_slow"], "signal"] = 1
        df.loc[df["ema_fast"] < df["ema_slow"], "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register(
    "ema_crossover",
    {
        "backtest_cls": EMACrossoverStrategy,
        "param_space": {
            "ema_crossover_fast_period": {
                "type": "int",
                "low": 5,
                "high": 25
            },
            "ema_crossover_slow_period": {
                "type": "int",
                "low": 30,
                "high": 100
            }
        }
    }
)
