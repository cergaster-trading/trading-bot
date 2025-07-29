from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class RSIStrategy(StrategyBase):
    def __init__(self, df, rsi_rsi_period=14, rsi_overbought=70, rsi_oversold=30):
        self.df = df.copy()
        self.period = rsi_rsi_period
        self.overbought = rsi_overbought
        self.oversold = rsi_oversold
        self.name = "rsi"

    def generate_signals(self):
        df = self.df.copy()
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / (loss + 1e-10)
        df["rsi"] = 100 - (100 / (1 + rs))

        df["signal"] = 0
        df.loc[df["rsi"] < self.oversold, "signal"] = 1
        df.loc[df["rsi"] > self.overbought, "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register(
    "rsi",
    {
        "backtest_cls": RSIStrategy,
        "param_space": {
            "rsi_rsi_period": {"type": "int", "low": 5, "high": 30},
            "rsi_overbought": {"type": "int", "low": 60, "high": 90},
            "rsi_oversold": {"type": "int", "low": 10, "high": 40}
        }
    }
)
