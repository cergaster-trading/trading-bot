import os
import json
import logging
import shutil
from datetime import datetime
import subprocess

from backtest.optimize_ensemble import tune_symbol_ensemble

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# === Constants ===
PARAM_FILE = "ensemble_tuned_params.json"
BACKUP_DIR = "backups"
SYMBOLS = ["TSLA", "NVDA", "COIN", "PLTR"]

# === Ensure Backup Folder Exists ===
os.makedirs(BACKUP_DIR, exist_ok=True)

# === Backup Old JSON File ===
def backup_params():
    if os.path.exists(PARAM_FILE):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        backup_file = os.path.join(BACKUP_DIR, f"ensemble_tuned_params_{timestamp}.json")
        shutil.copyfile(PARAM_FILE, backup_file)
        logger.info(f"✅ Backed up old params to {backup_file}")

# === Save Summary Report ===
def save_summary_report(summary):
    summary_path = os.path.join(BACKUP_DIR, f"summary_{datetime.now().strftime('%Y-%m-%d')}.txt")
    with open(summary_path, 'w') as f:
        f.write(summary)
    logger.info(f"📃 Saved summary report to {summary_path}")

# === Main Tuning Script ===
def main():
    logger.info("\U0001f680 Starting Daily Optimization for All Symbols")

    backup_params()
    all_results = {}

    for symbol in SYMBOLS:
        logger.info(f"⏳ Tuning {symbol}...")
        result = tune_symbol_ensemble(symbol, initial_cash=17500.0, trials=10)
        all_results[symbol] = result

    # Save final summary
    summary = "\n".join([
        f"{symbol} -> Best Value: {res['value']:.2f}\nParams: {json.dumps(res['params'], indent=2)}"
        for symbol, res in all_results.items()
    ])
    logger.info(f"📊 Summary:\n{summary}")
    save_summary_report(summary)

    # Restart the bot
    logger.info("🔄 Restarting trading bot with updated parameters...")
    subprocess.Popen(["python", "trading_bot.py"])

if __name__ == "__main__":
    main()
