# indicators/stochastic.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class StochasticStrategy(StrategyBase):
    def __init__(self, df, stochastic_k_period=14, stochastic_d_period=3,
                 stochastic_lower_bound=20, stochastic_upper_bound=80):
        self.df = df.copy()
        self.k = stochastic_k_period
        self.d = stochastic_d_period
        self.lower = stochastic_lower_bound
        self.upper = stochastic_upper_bound
        self.name = "stochastic"

    def generate_signals(self):
        df = self.df.copy()

        low_min = df["low"].rolling(self.k).min()
        high_max = df["high"].rolling(self.k).max()
        df["%K"] = 100 * (df["close"] - low_min) / (high_max - low_min + 1e-10)
        df["%D"] = df["%K"].rolling(self.d).mean()

        df["signal"] = 0
        df.loc[(df["%K"] > df["%D"]) & (df["%K"] < self.lower), "signal"] = 1
        df.loc[(df["%K"] < df["%D"]) & (df["%K"] > self.upper), "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register("stochastic", {
    "backtest_cls": StochasticStrategy,
    "param_space": {
        "stochastic_k_period": {
            "type": "int",
            "low": 5,
            "high": 30
        },
        "stochastic_d_period": {
            "type": "int",
            "low": 2,
            "high": 10
        },
        "stochastic_lower_bound": {
            "type": "int",
            "low": 10,
            "high": 40
        },
        "stochastic_upper_bound": {
            "type": "int",
            "low": 60,
            "high": 90
        }
    }
})
