# ingest_data.py
import os
import pandas as pd
import yfinance as yf
import config

DATA_DIR = "data"

def fetch_and_save(symbol):
    """
    Download historical daily bars from START_DATE to END_DATE
    and save to data/{symbol}_daily.csv
    """
    print(f"→ Fetching DAILY {symbol} from {config.START_DATE} to {config.END_DATE}…")
    df = yf.download(
        symbol,
        start=config.START_DATE,
        end=config.END_DATE,
        interval="1d",
        progress=False
    )
    if df.empty:
        print(f"⚠️ No daily data for {symbol}.")
        return

    path = os.path.join(DATA_DIR, f"{symbol}_daily.csv")
    df.to_csv(path)
    print(f"✓ Saved {len(df)} rows to {path}")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for sym in config.SYMBOLS:
        try:
            fetch_and_save(sym)
        except Exception as e:
            print(f"❗ Failed to fetch {sym}: {e}")

if __name__ == "__main__":
    main()
