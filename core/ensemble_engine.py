import pandas as pd
import logging
from indicators import (
    rsi, macd, bollinger, ema_crossover,
    sma_rsi, stochastic, supertrend, adx_di
)

logger = logging.getLogger(__name__)

# Strategy name → StrategyClass mapping
STRATEGY_CLASSES = {
    "rsi": rsi.StrategyClass,
    "macd": macd.StrategyClass,
    "bollinger": bollinger.StrategyClass,
    "ema_crossover": ema_crossover.StrategyClass,
    "sma_rsi": sma_rsi.StrategyClass,
    "stochastic": stochastic.StrategyClass,
    "supertrend": supertrend.StrategyClass,
    "adx_di": adx_di.StrategyClass,
}

def generate_blended_signal(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()
    total_weight = 0
    blended = pd.Series(0, index=df.index, dtype=float)

    for name, StrategyClass in STRATEGY_CLASSES.items():
        enabled = config.get(f"{name}_enabled", False)
        weight = config.get(f"{name}_weight", 0.0)

        if not enabled or weight <= 0:
            continue

        # Extract strategy-specific params
        strat_params = {
            k.replace(f"{name}_", ""): v
            for k, v in config.items()
            if k.startswith(f"{name}_")
        }

        try:
            strategy = StrategyClass(strat_params)
            signal_df = strategy.generate_signals(df)
            if "signal" not in signal_df.columns:
                raise ValueError(f"Strategy {name} missing 'signal' column.")

            weighted_signal = signal_df['signal'].fillna(0) * weight
            blended += weighted_signal
            total_weight += weight
            logger.debug(f"✅ {name} signal blended with weight {weight}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to generate signal for {name}: {e}")

    if total_weight > 0:
        blended /= total_weight

    df['blended_signal'] = blended.round().clip(-1, 1)
    return df[['blended_signal']]
