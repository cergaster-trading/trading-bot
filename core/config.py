import os
import json
from dotenv import load_dotenv

# === Load environment variables from .env ===
load_dotenv()

# === Load API keys from environment ===
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
USE_PAPER = os.getenv("USE_PAPER", "true").lower() == "true"

# === Set Alpaca base URL based on paper/live setting ===
if USE_PAPER:
    ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
else:
    ALPACA_BASE_URL = "https://api.alpaca.markets"

# === JSON Parameters File ===
PARAMS_FILE = "ensemble_tuned_params.json"

# === Load ensemble-tuned parameters from file ===
def load_ensemble_params():
    try:
        with open(PARAMS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

# === Get enabled trading symbols ===
def get_symbols():
    params = load_ensemble_params()
    return [
    symbol for symbol, cfg in params.items()
    if isinstance(cfg, dict) and cfg.get("enabled", True)
]

# === Get configuration dictionary for a symbol ===
def get_symbol_config(symbol):
    params = load_ensemble_params()
    return params.get(symbol.upper(), {})

# === Get initial cash allocation for a symbol ===
def get_initial_cash(symbol):
    cfg = get_symbol_config(symbol)
    return cfg.get("initial_cash", 17500.0)

# === Get trading interval (in minutes) for a symbol ===
def get_interval_minutes(symbol):
    cfg = get_symbol_config(symbol)
    return cfg.get("interval_minutes", 1)

# === Return API key bundle for AlpacaBroker ===
def get_api_keys(config=None):
    return {
        "API_KEY": ALPACA_API_KEY,
        "API_SECRET": ALPACA_SECRET_KEY,
        "BASE_URL": ALPACA_BASE_URL
    }
