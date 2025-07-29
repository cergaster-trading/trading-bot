# append_daily.py
import os
import pandas as pd
import yfinance as yf
import config
from datetime import datetime, timedelta

DATA_DIR = "data"

def append_symbol(symbol):
    path = os.path.join(DATA_DIR, f"{symbol}_daily.csv")

def append_symbol(symbol):
    path = os.path.join(DATA_DIR, f"{symbol}_daily.csv")

    # 1) Load & parse the CSV’s first column as the date
    raw = pd.read_csv(path)
    date_col = raw.columns[0]
    raw[date_col] = pd.to_datetime(raw[date_col], errors='coerce')
    raw = raw.dropna(subset=[date_col])
    df = raw.set_index(date_col).sort_index()
    if df.empty:
        print(f"⚠️ No valid timestamped rows in {symbol}_daily.csv")
        return

    # 2) Determine start/end
    last_date = df.index.max().date()
    start     = last_date + timedelta(days=1)
    end       = datetime.utcnow().date()
    if start > end:
        print(f"{symbol}: already up to date ({last_date})")
        return

    print(f"{symbol}: fetching {start} → {end}")
    new_df = yf.download(
        symbol,
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),
        interval="1d",
        progress=False
    )
    if new_df.empty:
        print(f"⚠️ No new data for {symbol}")
        return

    # 3) Append, dedupe, save
    combined = pd.concat([df, new_df])
    combined = combined[~combined.index.duplicated(keep='first')]
    combined.to_csv(path)
    print(f"✓ Appended {len(new_df)} rows to {path}")


def main():
    for sym in config.SYMBOLS:
        try:
            append_symbol(sym)
        except Exception as e:
            print(f"❗ Error for {sym}: {e}")

if __name__ == "__main__":
    main()
