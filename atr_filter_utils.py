# atr_filter_utils.py
"""
Utilities to compute ATR ratio and apply volatility-based trading regime filters.
"""

import pandas as pd


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Compute Average True Range (ATR).

    Parameters:
    - df: DataFrame with 'High', 'Low', 'Close' columns
    - period: lookback window for ATR (default: 14)

    Returns:
    - pd.Series of ATR values
    """
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift(1)).abs()
    low_close = (df['Low'] - df['Close'].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def apply_atr_regime(df: pd.DataFrame,
                     short_period: int = 50,
                     long_period: int = 200,
                     upper_thresh: float = 1.2,
                     lower_thresh: float = 0.8) -> tuple[pd.Series, pd.Series]:
    """
    Classify volatility regimes based on ATR ratio (short/long).

    Parameters:
    - df: DataFrame with 'High', 'Low', 'Close' columns
    - short_period: short ATR lookback (default: 50)
    - long_period: long ATR lookback (default: 200)
    - upper_thresh: threshold for aggressive regime
    - lower_thresh: threshold for conservative regime

    Returns:
    - regime: pd.Series with values -1 (conservative), 0 (neutral), 1 (aggressive)
    - atr_ratio: pd.Series of ATR short / ATR long
    """
    atr_short = compute_atr(df, short_period)
    atr_long = compute_atr(df, long_period)
    atr_ratio = atr_short / atr_long

    regime = pd.Series(0, index=df.index)
    regime[atr_ratio > upper_thresh] = 1
    regime[atr_ratio < lower_thresh] = -1

    return regime, atr_ratio
