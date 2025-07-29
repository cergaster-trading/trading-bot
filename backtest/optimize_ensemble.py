import yfinance as yf
import pandas as pd
import numpy as np
import optuna
import json
import argparse

from indicators.strategy_base import StrategyFactory
import indicators.registry  # Ensures all strategies are registered

PARAMS_FILE = "ensemble_tuned_params.json"

def run_optimize_ensemble(symbol, trials):
    print(f"\n🎯 Running ENSEMBLE optimization for {symbol} with {trials} trials...")

    # === Download and clean data ===
    df = yf.download(symbol, period="1y", interval="1d")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Adj Close": "adj_close"
    }, inplace=True)
    df = df.dropna().copy()

    # === Collect all registered strategies ===
    all_strategies = StrategyFactory.get_all().items()

    def objective(trial):
        strategy_classes = []
        strategy_params = []
        strategy_weights = {}

        for name, entry in all_strategies:
            cls = entry.get("backtest_cls")
            param_space = entry.get("param_space", {})

            # ✅ Defensive check for malformed registrations
            if cls is None or not callable(cls):
                raise TypeError(f"Strategy '{name}' has an invalid backtest_cls: {cls}")

            params = {}
            for param_name, param_info in param_space.items():
                full_param_name = f"{name}_{param_name}"
                if param_info["type"] == "int":
                    params[param_name] = trial.suggest_int(full_param_name, param_info["low"], param_info["high"])
                elif param_info["type"] == "float":
                    params[param_name] = trial.suggest_float(full_param_name, param_info["low"], param_info["high"], log=param_info.get("log", False))
                elif param_info["type"] == "categorical":
                    params[param_name] = trial.suggest_categorical(full_param_name, param_info["choices"])

            strategy_classes.append(cls)
            strategy_params.append(params)

            weight_name = f"{name}_weight"
            strategy_weights[weight_name] = trial.suggest_float(weight_name, 0.0, 1.0)

        # === SL/TP Meta Params ===
        sl_multiplier = trial.suggest_float("sl_multiplier", 0.5, 3.0)
        tp_multiplier = trial.suggest_float("tp_multiplier", 0.5, 5.0)
        meta_params = {"sl_multiplier": sl_multiplier, "tp_multiplier": tp_multiplier}

        from backtest.backtest import BacktestEngine
        engine = BacktestEngine(df, strategy_classes, strategy_params, strategy_weights, meta_params)
        result = engine.run()
        return result["sharpe_ratio"]

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=trials)

    # === Display and Save Best Result ===
    best_params = study.best_params
    print("\n✅ Best Parameters:")
    for k, v in best_params.items():
        print(f"  {k}: {v}")

    # Load or create output config
    try:
        with open(PARAMS_FILE, "r") as f:
            all_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_results = {}

    # Build config for current symbol
    strategies_config = []
    for name, entry in all_strategies:
        param_space = entry["param_space"]
        strategy_config = {
            "strategy": name,
            "params": {},
            "weight": best_params.get(f"{name}_weight", 0.0)
        }
        for param_name in param_space:
            full_param_name = f"{name}_{param_name}"
            strategy_config["params"][param_name] = best_params.get(full_param_name)
        strategies_config.append(strategy_config)

    all_results[symbol] = {
        "strategies": strategies_config,
        "sl_multiplier": best_params.get("sl_multiplier", 2.0),
        "tp_multiplier": best_params.get("tp_multiplier", 3.0)
    }

    with open(PARAMS_FILE, "w") as f:
        json.dump(all_results, f, indent=4)
    print(f"\n💾 Saved tuned parameters for {symbol} to {PARAMS_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, help="Symbol to optimize")
    parser.add_argument("--trials", type=int, default=25, help="Number of Optuna trials")
    args = parser.parse_args()

    run_optimize_ensemble(args.symbol.upper(), args.trials)
