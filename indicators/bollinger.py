# indicators/bollinger.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class BollingerStrategy(StrategyBase):
    def __init__(self, df, bollinger_window=20, bollinger_num_std=2.0):
        self.df = df.copy()
        self.window = bollinger_window
        self.num_std = bollinger_num_std
        self.name = "bollinger"

    def generate_signals(self):
        df = self.df.copy()
        df["ma"] = df["close"].rolling(window=self.window).mean()
        df["std"] = df["close"].rolling(window=self.window).std()

        df["upper_band"] = df["ma"] + self.num_std * df["std"]
        df["lower_band"] = df["ma"] - self.num_std * df["std"]

        df["signal"] = 0
        df.loc[df["close"] < df["lower_band"], "signal"] = 1
        df.loc[df["close"] > df["upper_band"], "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register("bollinger", {
    "backtest_cls": BollingerStrategy,
    "param_space": {
        "bollinger_window": {
            "type": "int",
            "low": 10,
            "high": 30
        },
        "bollinger_num_std": {
            "type": "float",
            "low": 1.0,
            "high": 3.0
        }
    }
})
