import os

INDICATORS_DIR = os.path.join(os.getcwd(), "indicators")

files = {
    "macd.py": '''import pandas as pd
import numpy as np

class MACDStrategy:
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["macd"] = df["ema_fast"] - df["ema_slow"]
        df["macd_signal"] = df["macd"].ewm(span=self.signal, adjust=False).mean()
        df["signal"] = np.where(df["macd"] > df["macd_signal"], 1, -1)
        return df["signal"].shift(1)
''',

    "rsi.py": '''import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(self.period).mean()
        avg_loss = pd.Series(loss).rolling(self.period).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        df["signal"] = np.where(rsi < self.oversold, 1,
                         np.where(rsi > self.overbought, -1, 0))
        return df["signal"].shift(1)
''',

    "bollinger.py": '''import pandas as pd
import numpy as np

class BollingerStrategy:
    def __init__(self, window=20, num_std=2):
        self.window = window
        self.num_std = num_std

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        df["sma"] = df["close"].rolling(self.window).mean()
        df["std"] = df["close"].rolling(self.window).std()
        df["upper"] = df["sma"] + self.num_std * df["std"]
        df["lower"] = df["sma"] - self.num_std * df["std"]
        df["signal"] = np.where(df["close"] < df["lower"], 1,
                         np.where(df["close"] > df["upper"], -1, 0))
        return df["signal"].shift(1)
''',

    "ema_crossover.py": '''import pandas as pd
import numpy as np

class EMACrossoverStrategy:
    def __init__(self, fast=12, slow=26):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["signal"] = np.where(df["ema_fast"] > df["ema_slow"], 1, -1)
        return df["signal"].shift(1)
''',

    "adx_di.py": '''import pandas as pd
import numpy as np

class ADXDIStrategy:
    def __init__(self, period=14):
        self.period = period

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        high, low, close = df["high"], df["low"], df["close"]
        prev_close = close.shift(1)

        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)

        up_move = high.diff()
        down_move = -low.diff()

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        tr_smooth = pd.Series(tr).rolling(self.period).sum()
        plus_dm_smooth = pd.Series(plus_dm).rolling(self.period).sum()
        minus_dm_smooth = pd.Series(minus_dm).rolling(self.period).sum()

        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        df["signal"] = np.where(plus
