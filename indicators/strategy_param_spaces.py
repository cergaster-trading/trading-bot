# indicators/strategy_param_spaces.py

strategy_param_spaces = {
    "rsi": {
        "rsi_rsi_period": (5, 30),
        "rsi_upper": (60, 90),
        "rsi_lower": (10, 40),
    },
    "macd": {
        "macd_fast_period": (5, 20),
        "macd_slow_period": (21, 50),
        "macd_signal_period": (5, 20),
    },
    "bollinger": {
        "bollinger_window": (10, 50),
        "bollinger_stddev": (1, 3),
    },
    "ema_crossover": {
        "ema_fast_period": (5, 20),
        "ema_slow_period": (21, 50),
    },
    "sma_rsi": {
        "sma_rsi_sma_period": (10, 50),
        "sma_rsi_rsi_period": (5, 30),
        "sma_rsi_rsi_upper": (60, 90),
        "sma_rsi_rsi_lower": (10, 40),
    },
    "supertrend": {
        "supertrend_period": (5, 20),
        "supertrend_multiplier": (1.0, 5.0),
    },
    "adx_di": {
        "adx_di_period": (10, 30),
    },
    "stochastic": {
        "stochastic_k": (5, 20),
        "stochastic_d": (3, 10),
    },
}

