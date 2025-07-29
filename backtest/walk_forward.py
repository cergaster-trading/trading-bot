# backtest/walk_forward.py

import os
import json
import yfinance as yf
import pandas as pd
import numpy as np
import argparse
import optuna
from datetime import timedelta
from indicators.strategy_base import StrategyFactory
import indicators.registry  # ensure all strategies are registered

PARAMS_FILE = "ensemble_tuned_params.json"


def load_params(symbol):
    with open(PARAMS_FILE, 'r') as f:
        all_params = json.load(f)
    return all_params.get(symbol)


def calculate_stats(equity_curve):
    returns = equity_curve.pct_change().dropna()
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
    peak = equity_curve.cummax()
    drawdown = (equity_curve - peak) / peak
    max_drawdown = drawdown.min()
    return sharpe, max_drawdown


def run_walk_forward(symbol, initial_cash, train_size_days=180, test_size_days=30):
    print(f"\n🔁 Starting walk-forward validation for {symbol}...\n")
    df = yf.download(symbol, period="2y", interval="1d", auto_adjust=False)
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
    }).dropna()

    params = load_params(symbol)
    if not params:
        print(f"❌ No parameters found for symbol: {symbol}")
        return

    strategies = []
    weights = {}
    strategy_params = []

    for strat in params["strategies"]:
        name = strat["strategy"]
        entry = StrategyFactory.get(name)
        if entry is None:
            raise ValueError(
                f"❌ Strategy '{name}' not found in StrategyFactory.\n"
                f"🧠 Tip: Check spelling and make sure it's registered in indicators/registry.py\n"
                f"🛠️  Available strategies: {list(StrategyFactory._registry.keys())}"
            )
        cls = entry["backtest_cls"]
        strategies.append(cls)
        strategy_params.append(strat["params"])
        weights[f"{name}_weight"] = strat["weight"]

    sl_multiplier = params.get("sl_multiplier", 2.0)
    tp_multiplier = params.get("tp_multiplier", 3.0)

    start_idx = 0
    stats_per_window = []
    total_days = len(df)

    while start_idx + train_size_days + test_size_days <= total_days:
        train_df = df.iloc[start_idx:start_idx + train_size_days]
        test_df = df.iloc[start_idx + train_size_days:start_idx + train_size_days + test_size_days].copy()

        blended_signal = np.zeros(len(test_df))

        for cls, strat_param in zip(strategies, strategy_params):
            strat = cls(pd.concat([train_df, test_df]).copy(), **strat_param)
            signal = strat.generate_signals().iloc[-len(test_df):]
            name_prefix = strat.name.split('_')[0]
            weight = weights.get(f"{name_prefix}_weight", 1.0)
            blended_signal += signal * weight

        test_df["signal"] = np.sign(blended_signal)

        # === Execute trades with SL/TP ===
        equity = [initial_cash]
        position = 0
        entry_price = 0

        for i in range(1, len(test_df)):
            row = test_df.iloc[i]
            prev = test_df.iloc[i - 1]
            signal = prev["signal"]

            price = row["close"]
            high = row["high"]
            low = row["low"]

            if position == 0 and signal == 1:
                position = equity[-1] / price
                entry_price = price
            elif position > 0:
                sl_price = entry_price * (1 - sl_multiplier / 100)
                tp_price = entry_price * (1 + tp_multiplier / 100)

                if low <= sl_price:
                    equity.append(position * sl_price)
                    position = 0
                elif high >= tp_price:
                    equity.append(position * tp_price)
                    position = 0
                elif signal == -1:
                    equity.append(position * price)
                    position = 0
                else:
                    equity.append(equity[-1])
            else:
                equity.append(equity[-1])

        if position > 0:
            equity[-1] = position * test_df.iloc[-1]["close"]

        eq_series = pd.Series(equity, index=test_df.index)
        sharpe, max_dd = calculate_stats(eq_series)

        print(f"📅 Window {start_idx}: Final=${eq_series.iloc[-1]:.2f}, Sharpe={sharpe:.2f}, MaxDD={max_dd:.2%}")
        stats_per_window.append({
            "start_date": test_df.index[0].strftime("%Y-%m-%d"),
            "end_date": test_df.index[-1].strftime("%Y-%m-%d"),
            "final_value": eq_series.iloc[-1],
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd
        })

        start_idx += test_size_days

    print("\n✅ Walk-forward complete.\n")
    for stat in stats_per_window:
        print(stat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--initial-cash", type=float, default=10000)
    args = parser.parse_args()

    run_walk_forward(args.symbol, args.initial_cash)
