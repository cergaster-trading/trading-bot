from indicators.sma_rsi import get_sma_rsi_params, calculate_sma_rsi_signal
from indicators.macd import get_macd_params, calculate_macd_signal
from indicators.bollinger import get_bollinger_params, calculate_bollinger_signal
from indicators.rsi import get_rsi_params, calculate_rsi_signal
from indicators.supertrend import get_supertrend_params, calculate_supertrend_signal
from indicators.adx_di import get_adx_params, calculate_adx_signal
from indicators.stochastic import get_stochastic_params, calculate_stochastic_signal
from indicators.ema_crossover import get_ema_crossover_params, calculate_ema_crossover_signal


def get_strategy_function(name: str):
    strategies = {
        "sma_rsi": (get_sma_rsi_params, calculate_sma_rsi_signal),
        "macd": (get_macd_params, calculate_macd_signal),
        "bollinger": (get_bollinger_params, calculate_bollinger_signal),
        "rsi": (get_rsi_params, calculate_rsi_signal),
        "supertrend": (get_supertrend_params, calculate_supertrend_signal),
        "adx_di": (get_adx_params, calculate_adx_signal),
        "stochastic": (get_stochastic_params, calculate_stochastic_signal),
        "ema_crossover": (get_ema_crossover_params, calculate_ema_crossover_signal),
    }
    return strategies.get(name)
