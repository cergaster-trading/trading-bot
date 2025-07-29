# monitoring/performance_summary.py

import numpy as np
import pandas as pd

def calculate_analyzers(df: pd.DataFrame):
    """
    Accepts a DataFrame with columns: ['strategy_return', 'equity_curve']
    Returns performance metrics: Sharpe, Max Drawdown, CAGR, etc.
    """
    result = {}
    returns = df["strategy_return"]

    result["sharpe"] = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252)

    # Max drawdown
    equity = df["equity_curve"]
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    result["max_drawdown"] = drawdown.min()

    # CAGR
    start_val = equity.iloc[0]
    end_val = equity.iloc[-1]
    num_years = len(equity) / 252
    result["cagr"] = (end_val / start_val) ** (1 / num_years) - 1

    # Total return
    result["total_return"] = end_val / start_val - 1

    return result
