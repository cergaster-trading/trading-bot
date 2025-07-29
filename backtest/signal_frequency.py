# signal_frequency.py

import sys
import pandas as pd
import yfinance as yf
import config    # your config.py

def fetch_and_features(symbol, period="60d", interval="15m"):
    """
    Download raw OHLC, compute fast/slow MAs and RSI, return a clean DataFrame.
    """
    raw = yf.download(
        symbol,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=True,
    )

    if raw.empty or "Close" not in raw.columns:
        raise RuntimeError("no data returned")

    # grab columns and rename
    df = raw[["Close", "High", "Low"]].rename(
        columns={"Close": "close", "High": "high", "Low": "low"}
    ).dropna()

    # moving avgs
    df["fast_ma"] = df["close"].rolling(config.FAST_MA).mean()
    df["slow_ma"] = df["close"].rolling(config.SLOW_MA).mean()

    # RSI
    delta = df["close"].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    p     = config.RSI_PERIOD
    avg_g = gain.ewm(alpha=1/p, adjust=False, min_periods=p).mean()
    avg_l = loss.ewm(alpha=1/p, adjust=False, min_periods=p).mean()
    rs    = avg_g / avg_l
    df["rsi"] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)
    return df

def count_signals(df):
    """
    Return (buy_count, sell_count) according to your crossover + RSI rules.
    """
    prev_fast = df["fast_ma"].shift(1)
    prev_slow = df["slow_ma"].shift(1)
    curr_fast = df["fast_ma"]
    curr_slow = df["slow_ma"]
    curr_rsi  = df["rsi"]

    buy_mask  = (prev_fast < prev_slow) & (curr_fast > curr_slow) & (curr_rsi < config.RSI_BUY_MAX)
    sell_mask = (prev_fast > prev_slow) & (curr_fast < curr_slow) & (curr_rsi > config.RSI_SELL_MIN)

    return int(buy_mask.sum()), int(sell_mask.sum())

if __name__ == "__main__":
    results = []
    for sym in config.SYMBOLS:
        try:
            df = fetch_and_features(sym)
            buys, sells = count_signals(df)
            results.append({
                "symbol":       sym,
                "data_points":  len(df),
                "buy_signals":  buys,
                "sell_signals": sells,
                "buy_%":        f"{buys/len(df)*100:.2f}%",
                "sell_%":       f"{sells/len(df)*100:.2f}%",
            })
        except Exception as e:
            print(f"⚠️  {sym}: {e}")

    if not results:
        print("\n❌ No symbols succeeded — check your internet connection or symbol list.")
        sys.exit(1)

    summary = pd.DataFrame(results)
    print("\nSignal frequency over last 60 days (15m bars):\n")
    print(summary.to_string(index=False))
