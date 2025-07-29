# regime_filter.py

import pandas as pd
import numpy as np

def apply_volume_filter(df: pd.DataFrame, volume_ratio: float = 1.5) -> pd.DataFrame:
    """
    Adds a 'volume_pass' column to the DataFrame indicating whether current volume
    is greater than volume_ratio × 20-day average volume.
    """
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['volume_pass'] = df['volume'] > (df['avg_volume'] * volume_ratio)
    return df


def apply_atr_regime(df: pd.DataFrame, window: int = 14, z_threshold: float = 0.5):
    """
    Adds ATR-based volatility regime classification.

    Returns:
        regime: Series with values:
            -1 = low volatility (conservative)
             0 = neutral
             1 = high volatility (aggressive)
        atr: Series of ATR values
    """
    high = df['high']
    low = df['low']
    close = df['close']

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=window).mean()

    z_scores = (atr - atr.mean()) / atr.std()
    regime = pd.cut(z_scores, bins=[-np.inf, -z_threshold, z_threshold, np.inf], labels=[-1, 0, 1]).astype(int)

    return regime, atr
