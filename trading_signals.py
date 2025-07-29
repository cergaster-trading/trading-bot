import pandas as pd
import json
import os

PARAMS_PATH = "ensemble_tuned_params.json"

# ─── CACHED PARAM LOADER ───────────────────────────────────────────────────────
def load_params(symbol):
    if not os.path.exists(PARAMS_PATH):
        return None
    with open(PARAMS_PATH, "r") as f:
        data = json.load(f)
    return data.get(symbol)

# ─── SIGNAL GENERATION ─────────────────────────────────────────────────────────
def get_trading_signal(df: pd.DataFrame, symbol: str) -> str | None:
    if df.shape[0] < 2:
        return None

    params = load_params(symbol)
    if not params:
        return None

    sma_fast = params.get("sma_fast", 10)
    sma_slow = params.get("sma_slow", 30)
    rsi_period = params.get("rsi_period", 14)

    df = df.copy()
    df["sma_fast"] = df["close"].rolling(window=sma_fast).mean()
    df["sma_slow"] = df["close"].rolling(window=sma_slow).mean()
    df["rsi"] = compute_rsi(df["close"], rsi_period)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # SMA signal
    sma_cross_up = prev["sma_fast"] < prev["sma_slow"] and last["sma_fast"] > last["sma_slow"]
    sma_cross_down = prev["sma_fast"] > prev["sma_slow"] and last["sma_fast"] < last["sma_slow"]

    # RSI filter
    rsi_buy = last["rsi"] < 70
    rsi_sell = last["rsi"] > 30

    if sma_cross_up and rsi_buy:
        return "buy"
    if sma_cross_down and rsi_sell:
        return "sell"

    return None

# ─── RSI HELPER ────────────────────────────────────────────────────────────────
def compute_rsi(series, period):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))