# indicators/adx_di.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd
import numpy as np


class ADXDIStrategy(StrategyBase):
    def __init__(self, df, di_adx_period=14, di_adx_threshold=20):
        self.df = df.copy()
        self.period = di_adx_period
        self.threshold = di_adx_threshold
        self.name = "adx_di"

    def generate_signals(self):
        df = self.df.copy()

        df["plus_dm"] = df["high"].diff()
        df["minus_dm"] = df["low"].diff() * -1

        df["plus_dm"] = np.where(
            (df["plus_dm"] > df["minus_dm"]) & (df["plus_dm"] > 0),
            df["plus_dm"], 0
        )
        df["minus_dm"] = np.where(
            (df["minus_dm"] > df["plus_dm"]) & (df["minus_dm"] > 0),
            df["minus_dm"], 0
        )

        tr1 = df["high"] - df["low"]
        tr2 = abs(df["high"] - df["close"].shift())
        tr3 = abs(df["low"] - df["close"].shift())
        df["tr"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = df["tr"].rolling(self.period).mean()
        plus_di = 100 * df["plus_dm"].rolling(self.period).mean() / atr
        minus_di = 100 * df["minus_dm"].rolling(self.period).mean() / atr

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        adx = dx.rolling(self.period).mean()

        df["signal"] = 0
        df.loc[(plus_di > minus_di) & (adx > self.threshold), "signal"] = 1
        df.loc[(minus_di > plus_di) & (adx > self.threshold), "signal"] = -1

        return df["signal"]


# Register strategy
StrategyFactory.register("adx_di", {
    "backtest_cls": ADXDIStrategy,
    "param_space": {
        "di_adx_period": {
            "type": "int",
            "low": 5,
            "high": 25
        },
        "di_adx_threshold": {
            "type": "int",
            "low": 10,
            "high": 40
        }
    }
})
