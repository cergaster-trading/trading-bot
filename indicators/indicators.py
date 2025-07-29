from indicators.macd import calculate_macd_signal
from indicators.rsi import calculate_rsi_signal
from indicators.bollinger import calculate_bollinger_signal
from indicators.ema_crossover import calculate_ema_crossover_signal
from indicators.adx_di import calculate_adx_signal
from indicators.supertrend import calculate_supertrend_signal
from indicators.stochastic import calculate_stochastic_signal

def get_signal_function(strategy_name):
    signal_functions = {
        "macd": calculate_macd_signal,
        "rsi": calculate_rsi_signal,
        "bollinger": calculate_bollinger_signal,
        "ema_crossover": calculate_ema_crossover_signal,
        "adx_di": calculate_adx_signal,
        "supertrend": calculate_supertrend_signal,
        "stochastic": calculate_stochastic_signal,
    }
    return signal_functions.get(strategy_name)
