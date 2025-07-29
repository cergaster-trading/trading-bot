import os
import sys
import time
import json
import pytz
import logging
import schedule
from datetime import datetime

import core.config as config
from core.data_loader import get_price_data
from core.broker import AlpacaBroker
from core.utils import is_market_open
from core.trade_cycle import run_trade_cycle
from monitoring.prometheus_metrics import start_prometheus_server
from monitoring.telegram_utils import send_telegram_alert
from indicators.strategy_base import StrategyFactory
import indicators.registry

# === Logging Setup ===
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_FILE = "logs/trading_bot.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# === Globals ===
broker = AlpacaBroker(config)
TIMEZONE = pytz.timezone("US/Eastern")
PARAMS_FILE = "ensemble_tuned_params.json"
cached_params_timestamp = None
ensemble_params = {}

# === Load Tuned Parameters ===
def load_ensemble_params():
    global ensemble_params, cached_params_timestamp
    try:
        current_timestamp = os.path.getmtime(PARAMS_FILE)
        if current_timestamp != cached_params_timestamp:
            with open(PARAMS_FILE, 'r') as f:
                ensemble_params = json.load(f)
            cached_params_timestamp = current_timestamp
            logger.info("🔄 Reloaded ensemble parameters from file.")
    except FileNotFoundError:
        logger.warning("⚠️ ensemble_tuned_params.json not found.")
        ensemble_params = {}

# === Main Trading Loop ===
def trading_loop():
    if not is_market_open():
        logger.info("📉 Market is closed. Skipping trade cycle.")
        return

    load_ensemble_params()

    symbols = config.get_symbols()

    for symbol in symbols:
        try:
            logger.info(f"\n=== Executing trade cycle for {symbol} ===")
            cfg = ensemble_params.get(symbol, {})
            if not cfg:
                logger.warning(f"⚠️ No tuned parameters found for {symbol}. Skipping.")
                continue

            strategy_list = cfg.get("strategies", [])
            strategy_classes = []
            strategy_params = []
            strategy_weights = {}

            df = get_price_data(symbol)
            if df is None or df.empty:
                logger.warning(f"No data returned for {symbol}. Skipping.")
                continue

            for strat_cfg in strategy_list:
                name = strat_cfg["strategy"]
                params = strat_cfg["params"]
                weight = strat_cfg.get("weight", 1.0)

                strategy = StrategyFactory.create(name, df.copy(), **params)
                strategy_classes.append(strategy.__class__)
                strategy_params.append(params)
                strategy_weights[f"{name}_weight"] = weight

            meta_params = {
                "sl_multiplier": cfg.get("sl_multiplier", 2.0),
                "tp_multiplier": cfg.get("tp_multiplier", 3.0),
            }

            allocation_pct = cfg.get("meta", {}).get("allocation_pct", 0.25)

            run_trade_cycle(
                symbol,
                broker,
                cfg,
                allocation_pct,
                strategy_classes,
                strategy_params,
                strategy_weights,
                meta_params
            )

        except Exception as e:
            logger.error(f"❌ Error running trade cycle for {symbol}: {e}")
            send_telegram_alert(f"❌ Error with {symbol}: {e}")

# === Entry Point ===
if __name__ == "__main__":
    logger.info("🚀 Starting multi-symbol trading bot...")
    start_prometheus_server()
    schedule.every(1).minutes.do(trading_loop)

    while True:
        schedule.run_pending()
        time.sleep(1)
