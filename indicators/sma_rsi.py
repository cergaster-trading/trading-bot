# indicators/sma_rsi.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class SMARsiStrategy(StrategyBase):
    def __init__(self, df, sma_rsi_period=14, sma_window=20, sma_rsi_threshold=50):
        self.df = df.copy()
        self.rsi_period = sma_rsi_period
        self.sma_window = sma_window
        self.threshold = sma_rsi_threshold
        self.name = "sma_rsi"

    def generate_signals(self):
        df = self.df.copy()

        # RSI calculation
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(self.rsi_period).mean()
        avg_loss = loss.rolling(self.rsi_period).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        df["rsi"] = 100 - (100 / (1 + rs))

        # SMA calculation
        df["sma"] = df["close"].rolling(self.sma_window).mean()

        df["signal"] = 0
        df.loc[(df["close"] > df["sma"]) & (df["rsi"] > self.threshold), "signal"] = 1
        df.loc[(df["close"] < df["sma"]) & (df["rsi"] < self.threshold), "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register("sma_rsi", {
    "backtest_cls": SMARsiStrategy,
    "param_space": {
        "sma_rsi_period": {
            "type": "int",
            "low": 5,
            "high": 30
        },
        "sma_window": {
            "type": "int",
            "low": 10,
            "high": 50
        },
        "sma_rsi_threshold": {
            "type": "int",
            "low": 40,
            "high": 60
        }
    }
})
