# indicators/macd.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class MACDStrategy(StrategyBase):
    def __init__(self, df, macd_fast_period=12, macd_slow_period=26, macd_signal_period=9):
        self.df = df.copy()
        self.fast = macd_fast_period
        self.slow = macd_slow_period
        self.signal = macd_signal_period
        self.name = "macd"

    def generate_signals(self):
        df = self.df.copy()

        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["macd"] = df["ema_fast"] - df["ema_slow"]
        df["macd_signal"] = df["macd"].ewm(span=self.signal, adjust=False).mean()

        df["signal"] = 0
        df.loc[df["macd"] > df["macd_signal"], "signal"] = 1
        df.loc[df["macd"] < df["macd_signal"], "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register("macd", {
    "backtest_cls": MACDStrategy,
    "param_space": {
        "macd_fast_period": {
            "type": "int",
            "low": 5,
            "high": 15
        },
        "macd_slow_period": {
            "type": "int",
            "low": 20,
            "high": 40
        },
        "macd_signal_period": {
            "type": "int",
            "low": 5,
            "high": 15
        }
    }
})
