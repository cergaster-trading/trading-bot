import pandas as pd
import numpy as np
from indicators.strategy_base import StrategyFactory
import indicators.registry  # ensure all strategies are registered

def run_trade_cycle(symbol, price_data, ensemble_params):
    df = price_data.copy()
    df.columns = [col.lower() for col in df.columns]

    strategy_specs = ensemble_params.get(symbol.upper(), {}).get("strategies", [])
    if not strategy_specs:
        return None

    blended_signal = np.zeros(len(df))
    for spec in strategy_specs:
        strategy_cls = StrategyFactory.get_class(spec["strategy"])
        if not strategy_cls:
            continue
        strategy = strategy_cls(df.copy(), **spec["params"])
        signal = strategy.generate_signals()

        weight_key = f"{spec['strategy'].split('_')[0].lower()}_weight"
        weight = spec.get("weight", 1.0)
        blended_signal += weight * signal

    final_signal = int(np.sign(blended_signal[-1]))
    return final_signal
