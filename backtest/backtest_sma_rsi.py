"""
Backtest a single symbol using SMA+RSI strategy, with slippage, commission, and ATR regime filtering.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Callable, Dict, Any
import config
from config import SYMBOLS, START_DATE, END_DATE, STARTING_CAPITAL
from backtest_utils import simulate_fill
from atr_filter_utils import apply_atr_regime


def backtest_symbol(
    symbol: str,
    params: Dict[str, int],
    fill_fn: Callable = simulate_fill,
    atr_short: int = 50,
    atr_long: int = 200,
    upper_thresh: float = 1.2,
    lower_thresh: float = 0.8
) -> Dict[str, Any]:
    """
    Simulates trading a single stock with SMA crossover + RSI filter, with regime-based filtering.

    Returns:
        dict: performance summary { 'symbol', 'total_return', 'sharpe', 'trades' }
    """

    # === 1) Historical data
    df = yf.download(symbol, start=START_DATE, end=END_DATE, auto_adjust=True)
    df.dropna(inplace=True)

    # === 2) ATR regime
    df["regime"], df["atr_ratio"] = apply_atr_regime(
        df, short_period=atr_short, long_period=atr_long,
        upper_thresh=upper_thresh, lower_thresh=lower_thresh
    )

    # === 3) Indicators
    df["fast"] = df["Close"].rolling(params["fast"]).mean()
    df["slow"] = df["Close"].rolling(params["slow"]).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    period = params["rsi_period"]
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)

    # === 4) Trading signals
    df["signal"] = 0
    buy_cond = (
        (df["fast"].shift(1) <= df["slow"].shift(1)) &
        (df["fast"] > df["slow"]) &
        (df["rsi"] < params["rsi_buy_max"])
    )
    sell_cond = (
        (df["fast"].shift(1) >= df["slow"].shift(1)) &
        (df["fast"] < df["slow"]) &
        (df["rsi"] > params["rsi_sell_min"])
    )
    df.loc[buy_cond, "signal"] = 1
    df.loc[sell_cond, "signal"] = -1

    # === 5) Simulation loop
    cash = STARTING_CAPITAL
    position = 0
    portfolio_values = []
    trades = 0

    closes = df["Close"].values
    regimes = df["regime"].values
    signals = df["signal"].values

    for i in range(len(df)):
        if regimes[i] == -1:
            # conservative regime, skip trading
            portfolio_values.append(cash + position * closes[i])
            continue

        qty = int(signals[i])
        if qty != 0:
            fill_price, net_cash = fill_fn(symbol, closes[i], qty)
            cash -= net_cash
            position += qty
            trades += 1

        portfolio_values.append(cash + position * closes[i])

    # === 6) Metrics
    vals = np.array(portfolio_values, dtype=float)

    if len(vals) > 1:
        returns = vals[1:] / vals[:-1] - 1
    else:
        returns = np.array([])

    total_return = (vals[-1] - STARTING_CAPITAL) / STARTING_CAPITAL
    vol = returns.std(ddof=0)
    sharpe = (returns.mean() / vol * np.sqrt(252)) if vol != 0 else 0.0

    return {
        "symbol": symbol,
        "total_return": total_return,
        "sharpe": sharpe,
        "trades": trades
    }


# === Optional test run ===
if __name__ == "__main__":
    default_params = {
        "fast":        config.FAST_MA,
        "slow":        config.SLOW_MA,
        "rsi_period":  config.RSI_PERIOD,
        "rsi_buy_max": config.RSI_BUY_MAX,
        "rsi_sell_min": config.RSI_SELL_MIN,
    }

    for sym in SYMBOLS:
        result = backtest_symbol(sym, default_params)
        print(
            f"{sym}: Return = {result['total_return'] * 100:.2f}%, "
            f"Sharpe = {result['sharpe']:.2f}, "
            f"Trades = {result['trades']}"
        )
