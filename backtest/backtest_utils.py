import pandas as pd
import numpy as np
from backtest.backtest import BacktestEngine
from indicators.strategy_base import StrategyBase
from monitoring.performance_summary import calculate_analyzers

def run_backtest(
    df: pd.DataFrame,
    strategy_classes: list,
    strategy_params_list: list,
    initial_cash: float = 17500.0,
    weights: list = None
) -> dict:
    """
    Run a blended multi-strategy backtest with weighted signal averaging.

    Args:
        df (pd.DataFrame): OHLCV historical data
        strategy_classes (list): List of StrategyBase subclasses
        strategy_params_list (list): List of parameter dicts (1 per strategy)
        initial_cash (float): Starting cash value
        weights (list): Optional list of floats (same length as strategies)

    Returns:
        dict: Result with equity curve, final value, sharpe, drawdown, return
    """
    assert len(strategy_classes) == len(strategy_params_list), "Mismatch in strategies and parameters"
    num_strategies = len(strategy_classes)
    weights = weights or [1.0] * num_strategies
    assert len(weights) == num_strategies, "Weight list length mismatch"

    # === Generate signals from each strategy ===
    signals = []
    for strategy_class, params in zip(strategy_classes, strategy_params_list):
        strategy = strategy_class(params)
        signal_df = strategy.generate_signals(df.copy())
        signals.append(signal_df["signal"])

    # === Weighted signal blending ===
    weighted = sum(sig * w for sig, w in zip(signals, weights))
    weight_sum = sum(weights)
    combined_signal = pd.DataFrame(index=df.index)
    combined_signal["signal"] = np.round(weighted / weight_sum)

    # === Run backtest ===
    engine = BacktestEngine(df, combined_signal["signal"], initial_cash)
    result_df, final_value = engine.run()

    # === Analyze performance ===
    analyzers = calculate_analyzers(result_df, initial_cash)

    return {
        "final_value": final_value,
        "sharpe": analyzers.get("sharpe"),
        "max_drawdown": analyzers.get("max_drawdown"),
        "return": analyzers.get("total_return"),
        "equity_curve": result_df,
        "signals": combined_signal,
    }
