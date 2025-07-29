# indicators/supertrend.py

from indicators.strategy_base import StrategyFactory, StrategyBase
import pandas as pd


class SupertrendStrategy(StrategyBase):
    def __init__(self, df, supertrend_atr_period=10, supertrend_multiplier=3.0):
        self.df = df.copy()
        self.atr_period = supertrend_atr_period
        self.multiplier = supertrend_multiplier
        self.name = "supertrend"

    def generate_signals(self):
        df = self.df.copy()

        hl = df["high"] - df["low"]
        hc = (df["high"] - df["close"].shift()).abs()
        lc = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        atr = tr.rolling(self.atr_period).mean()

        hl2 = (df["high"] + df["low"]) / 2
        upperband = hl2 + self.multiplier * atr
        lowerband = hl2 - self.multiplier * atr

        direction = [0]
        for i in range(1, len(df)):
            prev_dir = direction[-1]
            close = df["close"].iloc[i]
            prev_upper = upperband.iloc[i - 1]
            prev_lower = lowerband.iloc[i - 1]

            if prev_dir == -1 and close > prev_upper:
                direction.append(1)
            elif prev_dir == 1 and close < prev_lower:
                direction.append(-1)
            else:
                direction.append(prev_dir)

        df["signal"] = direction
        return df["signal"]


# Register strategy
StrategyFactory.register("supertrend", {
    "backtest_cls": SupertrendStrategy,
    "param_space": {
        "supertrend_atr_period": {
            "type": "int",
            "low": 5,
            "high": 20
        },
        "supertrend_multiplier": {
            "type": "float",
            "low": 1.0,
            "high": 5.0
        }
    }
})
