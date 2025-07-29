import os
import json
import logging
import yfinance as yf
import pandas as pd
import numpy as np
from indicators.strategy_base import StrategyFactory
import indicators.registry  # Ensures strategies are registered

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

PARAMS_FILE = "ensemble_tuned_params.json"

def load_ensemble_params(symbol):
    if not os.path.exists(PARAMS_FILE):
        logger.warning(f"{PARAMS_FILE} not found.")
        return [], [], {}, 2.0, 3.0

    with open(PARAMS_FILE, "r") as f:
        all_params = json.load(f)

    symbol_params = all_params.get(symbol)
    if not symbol_params:
        logger.warning(f"No parameters found for {symbol} in {PARAMS_FILE}")
        return [], [], {}, 2.0, 3.0

    strategies = []
    params_list = []
    weights = {}

    for entry in symbol_params.get("strategies", []):
        strategy_name = entry["strategy"]
        cls = StrategyFactory.get_strategy_class(strategy_name)
        if not cls:
            logger.warning(f"Strategy class not found: {strategy_name}")
            continue
        strategies.append(cls)
        params_list.append(entry["params"])
        weights[f"{strategy_name}_weight"] = entry["weight"]

    sl_multiplier = symbol_params.get("sl_multiplier", 2.0)
    tp_multiplier = symbol_params.get("tp_multiplier", 3.0)

    return strategies, params_list, weights, sl_multiplier, tp_multiplier


def run_backtest(symbol, initial_cash=17500):
    logger.info(f"📥 Downloading data for {symbol}...")
    df = yf.download(symbol, period="1y", interval="1d")
    df = df.rename(columns=str.lower)
    df.dropna(inplace=True)

    strategies, params_list, strategy_weights, sl, tp = load_ensemble_params(symbol)

    print(f"\n📦 Strategy Weights: {strategy_weights}")
    print(f"🎯 SL Multiplier: {sl} | TP Multiplier: {tp}")

    # Generate blended signals
    blended_signal = np.zeros(len(df))
    for cls, params in zip(strategies, params_list):
        strategy = cls(df.copy(), **params)
        signal = strategy.generate_signals()
        name = cls.__name__.replace("Strategy", "").lower()
        weight_key = f"{name}_weight"
        weight = strategy_weights.get(weight_key, 0)
        blended_signal += signal * weight

    # Normalize if weights > 1
    total_weight = sum(strategy_weights.values())
    if total_weight > 0:
        blended_signal /= total_weight

    # Binary signals: 1 (buy), -1 (sell), 0 (hold)
    df["signal"] = np.sign(blended_signal)

    print("\n📊 Blended signal distribution:")
    print(df["signal"].value_counts())

    # Simulate trades
    df["position"] = df["signal"].replace({-1: 0}).ffill().fillna(0)
    df["returns"] = df["position"].shift().astype(float) * df["close"].pct_change().fillna(0)
    df["equity"] = (1 + df["returns"]).cumprod() * initial_cash

    final_equity = df["equity"].iloc[-1]
    total_return = (final_equity - initial_cash) / initial_cash * 100
    sharpe = df["returns"].mean() / df["returns"].std() * np.sqrt(252) if df["returns"].std() != 0 else 0
    max_drawdown = ((df["equity"].cummax() - df["equity"]) / df["equity"].cummax()).max() * 100

    print("\n📊 Backtest Results:")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")

    print(f"\n📈 Symbol: {symbol}")
    print(f"Initial Cash: ${initial_cash:,.2f}")
    print(f"Final Equity: ${final_equity:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print("-" * 56)


if __name__ == "__main__":
    for symbol in ["TSLA", "NVDA", "PLTR", "COIN"]:
        print(f"\n≡ƒöä Running backtest for {symbol} with $17500 starting cash...")
        run_backtest(symbol)
