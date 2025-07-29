# backtest/optimize.py

import yfinance as yf
import pandas as pd
import numpy as np
import optuna
import json
import argparse
from indicators.strategy_base import StrategyFactory
import indicators.registry  # Ensure all strategies are registered

PARAMS_FILE = "ensemble_tuned_params.json"

def get_meta_param_space(symbol):
    if symbol == "COIN":
        return {
            "sl_multiplier": (1.2, 2.5),
            "tp_multiplier": (1.0, 2.0)
        }
    elif symbol == "PLTR":
        return {
            "sl_multiplier": (1.5, 3.0),
            "tp_multiplier": (1.2, 2.5)
        }
    elif symbol == "NVDA":
        return {
            "sl_multiplier": (1.5, 3.0),
            "tp_multiplier": (1.2, 2.5)
        }
    else:
        return {
            "sl_multiplier": (1.5, 3.0),
            "tp_multiplier": (1.2, 2.5)
        }

def run_optimize(symbol, strategy_name, trials):
    print(f"\n🔍 Optimizing {strategy_name.upper()} strategy for {symbol} using {trials} trials...")

    df = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
    df.rename(columns=str.lower, inplace=True)
    df = df.dropna().copy()

    strategy_config = StrategyFactory.get_config(strategy_name)
    meta_param_space = get_meta_param_space(symbol)

    def objective(trial):
        params = {}
        for param_name, bounds in strategy_config["param_space"].items():
            if isinstance(bounds, tuple) and len(bounds) == 2:
                if isinstance(bounds[0], int) and isinstance(bounds[1], int):
                    params[param_name] = trial.suggest_int(param_name, bounds[0], bounds[1])
                else:
                    params[param_name] = trial.suggest_float(param_name, bounds[0], bounds[1])

        sl = trial.suggest_float("sl_multiplier", *meta_param_space["sl_multiplier"])
        tp = trial.suggest_float("tp_multiplier", *meta_param_space["tp_multiplier"])

        strategy = strategy_config["backtest_cls"](df.copy(), **params)
        signal = strategy.generate_signals()

        position = 0
        entry_price = 0
        equity = 1.0
        peak = 1.0

        for i in range(1, len(df)):
            price = df["close"].iloc[i]
            prev_price = df["close"].iloc[i - 1]
            s = signal[i]

            if position == 0 and s == 1:
                position = 1
                entry_price = price
            elif position == 1:
                sl_trigger = entry_price * (1 - sl / 100)
                tp_trigger = entry_price * (1 + tp / 100)
                if price <= sl_trigger or price >= tp_trigger or s == -1:
                    pct_change = (price - entry_price) / entry_price
                    equity *= 1 + pct_change
                    peak = max(peak, equity)
                    position = 0

        return equity

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=trials)

    best = study.best_trial
    print("\n✅ Best Params Found:")
    for k, v in best.params.items():
        print(f"  {k}: {v}")

    try:
        with open(PARAMS_FILE, "r") as f:
            all_params = json.load(f)
    except FileNotFoundError:
        all_params = {}

    all_params[symbol] = {
        "strategies": [{
            "strategy": strategy_name,
            "params": {k: v for k, v in best.params.items() if k not in ("sl_multiplier", "tp_multiplier")},
            "weight": 1.0
        }],
        "sl_multiplier": best.params["sl_multiplier"],
        "tp_multiplier": best.params["tp_multiplier"]
    }

    with open(PARAMS_FILE, "w") as f:
        json.dump(all_params, f, indent=2)

    print(f"\n💾 Saved tuned strategy to {PARAMS_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True)
    parser.add_argument("--strategy", type=str, required=True)
    parser.add_argument("--trials", type=int, default=25)
    args = parser.parse_args()
    run_optimize(args.symbol, args.strategy, args.trials)
