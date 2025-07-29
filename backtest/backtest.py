# backtest/backtest.py

import pandas as pd
import numpy as np
import json
import yfinance as yf
import argparse

from indicators.strategy_base import StrategyFactory
import indicators.registry  # ensures all strategies are registered

PARAMS_FILE = "ensemble_tuned_params.json"


class BacktestEngine:
    def __init__(self, df, strategy_classes, strategy_params, strategy_weights, meta_params, debug=False):
        self.df = df.copy()
        self.strategy_classes = strategy_classes
        self.strategy_params = strategy_params
        self.strategy_weights = strategy_weights
        self.sl_multiplier = meta_params.get("sl_multiplier", 2.0)
        self.tp_multiplier = meta_params.get("tp_multiplier", 3.0)
        self.debug = debug

    def run(self):
        df = self.df.copy()
        blended_signal = np.zeros(len(df))

        for cls, params in zip(self.strategy_classes, self.strategy_params):
            strategy = cls(df.copy(), **params)
            signal = strategy.generate_signals()
            if signal is None:
                raise ValueError(f"❌ Strategy '{strategy.name}' returned None from generate_signals().")
            weight_key = f"{strategy.name}_weight"
            weight = self.strategy_weights.get(weight_key, 1.0)
            blended_signal += signal * weight

        df["signal"] = np.sign(blended_signal)
        df["equity"] = np.nan

        equity = 1.0
        position = 0
        entry_price = 0

        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]
            signal = prev["signal"]
            price = row["close"]
            high = row["high"]
            low = row["low"]

            if position == 0 and signal == 1:
                position = equity / price
                entry_price = price
                if self.debug:
                    sl = entry_price * (1 - self.sl_multiplier / 100)
                    tp = entry_price * (1 + self.tp_multiplier / 100)
                    print(f"[{row.name.date()}] BUY  @ {entry_price:.2f} | TP: {tp:.2f} | SL: {sl:.2f}")

            elif position > 0:
                sl_price = entry_price * (1 - self.sl_multiplier / 100)
                tp_price = entry_price * (1 + self.tp_multiplier / 100)

                if low <= sl_price:
                    equity = position * sl_price
                    position = 0
                    if self.debug:
                        print(f"[{row.name.date()}] EXIT via SL @ {sl_price:.2f}")
                elif high >= tp_price:
                    equity = position * tp_price
                    position = 0
                    if self.debug:
                        print(f"[{row.name.date()}] EXIT via TP @ {tp_price:.2f}")
                elif signal == -1:
                    equity = position * price
                    position = 0
                    if self.debug:
                        print(f"[{row.name.date()}] EXIT via Signal @ {price:.2f}")
                else:
                    df.at[df.index[i], "equity"] = equity
                    if self.debug:
                        print(f"[{row.name.date()}] HOLD | Price: {price:.2f}")
                    continue

            df.at[df.index[i], "equity"] = equity

        if position > 0:
            equity = position * df.iloc[-1]["close"]
            df.at[df.index[-1], "equity"] = equity
            if self.debug:
                print(f"[{df.index[-1].date()}] CLOSE REMAINING @ {df.iloc[-1]['close']:.2f}")

        df["equity"] = df["equity"].ffill()
        equity_curve = df["equity"]

        returns = equity_curve.pct_change().dropna()
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak
        max_drawdown = drawdown.min()

        print("\n📊 Backtest Results:")
        print(f"  Final Value     : {equity:.2f}")
        print(f"  Sharpe Ratio    : {sharpe:.2f}")
        print(f"  Max Drawdown    : {abs(max_drawdown):.2%}")


def load_params(symbol):
    with open(PARAMS_FILE, "r") as f:
        return json.load(f).get(symbol)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    df = yf.download(args.symbol.upper(), period="1y", interval="1d")
    df.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Volume": "volume"
    }, inplace=True)
    df.dropna(inplace=True)

    params = load_params(args.symbol.upper())
    if not params:
        print(f"❌ No parameters found for {args.symbol}")
        exit()

    strategies = []
    weights = {}
    strategy_params = []

    for strat in params["strategies"]:
        name = strat["strategy"]
        entry = StrategyFactory.get(name)
        if entry is None:
            raise ValueError(f"❌ Strategy '{name}' not found in registry.")
        if not isinstance(entry, dict) or "backtest_cls" not in entry:
            raise TypeError(f"❌ ERROR: Strategy '{name}' must be registered with 'backtest_cls'. Got: {type(entry)}")

        cls = entry["backtest_cls"]  # ✅ Fixed line
        strategies.append(cls)
        strategy_params.append(strat["params"])
        weights[f"{name}_weight"] = strat["weight"]

    meta_params = {
        "sl_multiplier": params.get("sl_multiplier", 2.0),
        "tp_multiplier": params.get("tp_multiplier", 3.0)
    }

    engine = BacktestEngine(df, strategies, strategy_params, weights, meta_params, debug=args.debug)
    engine.run()
