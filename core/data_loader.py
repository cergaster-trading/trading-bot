import yfinance as yf
import pandas as pd
from datetime import datetime
import logging

def get_price_data(symbol: str, start_date: str = "2023-01-01", end_date: str = None) -> pd.DataFrame:
    """
    Fetches daily historical price data for a symbol using yFinance.
    Falls back to flat columns: open, high, low, close, volume
    """
    try:
        logging.info(f"📥 Trying yFinance for {symbol}...")
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")

        df = yf.download(symbol, start=start_date, end=end_date, interval="1d", progress=False)

        # If tuple was returned accidentally (older yfinance bug workaround)
        if isinstance(df, tuple):
            df = df[0]

        if df.empty:
            raise ValueError("yFinance returned empty data")

        # Remove multi-index if it exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.rename(columns={c: c.lower() for c in df.columns})
        df.index = pd.to_datetime(df.index)
        df = df[['open', 'high', 'low', 'close', 'volume']]  # Enforce required columns only
        logging.info(f"✅ yFinance succeeded for {symbol}")
        return df

    except Exception as e:
        logging.warning(f"❌ Failed to get data from yFinance for {symbol}: {e}")
        return pd.DataFrame()
