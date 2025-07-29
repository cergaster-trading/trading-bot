import pandas as pd

def apply_atr_stop(df, period=14, multiplier=1.5):
    """
    Add ATR-based stop-loss bands to the DataFrame.
    """

    # Calculate True Range
    hl = df['high'] - df['low']
    hc = (df['high'] - df['close'].shift(1)).abs()
    lc = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

    # Calculate ATR
    atr = tr.rolling(window=period, min_periods=1).mean()
    df['atr'] = atr

    # Force close and atr to be Series (not accidentally DataFrames)
    close_series = df['close'].astype(float).squeeze()
    atr_series = df['atr'].astype(float).squeeze()

    # Compute stop bands
    df['upper_atr_band'] = close_series + atr_series * multiplier
    df['lower_atr_band'] = close_series - atr_series * multiplier

    return df
