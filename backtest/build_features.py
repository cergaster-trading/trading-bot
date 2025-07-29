# build_features.py
import os
import pandas as pd
import config

DATA_DIR     = "data"
FEATURES_DIR = "features"

def compute_features(symbol):
    """
    Read raw daily CSV, select core OHLCV, compute MA, RSI, ATR, and save features.
    """
    path = os.path.join(DATA_DIR, f"{symbol}_daily.csv")
    # 1) Load CSV and parse dates
    df = pd.read_csv(path, index_col=0, parse_dates=True)

    # 2) Keep only the core OHLCV columns
    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in {symbol}_daily.csv")
    df = df[required]

    print(f"\n--- {symbol} ---")
    print(f"Raw rows after cleaning: {len(df)}")
    print("Nulls before indicator calc:")
    print(df.isna().sum())

    # 3) Compute fast & slow moving averages
    df["fast_ma"] = df["Close"].rolling(config.FAST_MA).mean()
    df["slow_ma"] = df["Close"].rolling(config.SLOW_MA).mean()

    # 4) Compute RSI
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    period = config.RSI_PERIOD
    avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # 5) Compute ATR (14-day)
    high_low = df["High"] - df["Low"]
    high_cp  = (df["High"] - df["Close"].shift()).abs()
    low_cp   = (df["Low"]  - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()

    print("Nulls after indicator calc:")
    print(df.isna().sum())

    # 6) Drop warm-up NaNs and save
    feat = df.dropna()
    print(f"Rows after dropna: {len(feat)}")

    os.makedirs(FEATURES_DIR, exist_ok=True)
    out_path = os.path.join(FEATURES_DIR, f"{symbol}_daily_features.csv")
    feat.to_csv(out_path)
    print(f"✓ Built {len(feat)} feature rows for {symbol}")

def main():
    for sym in config.SYMBOLS:
        try:
            compute_features(sym)
        except Exception as e:
            print(f"❗ Error computing features for {sym}: {e}")

if __name__ == "__main__":
    main()
