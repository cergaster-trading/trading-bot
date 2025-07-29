import subprocess
import datetime
import logging

# === Setup Logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# === Symbols to Auto-Tune ===
symbols = ["TSLA", "NVDA", "PLTR", "COIN"]

# === Daily Timestamp ===
today = datetime.datetime.now().strftime("%Y-%m-%d")
logger.info(f"🚀 Starting daily auto-tuning for {today}...")

# === Trials and Capital Config ===
default_trials = 25
default_initial_cash = 17500.0

# === Run Ensemble Optimization ===
def run_ensemble_optimization(symbol):
    cmd = [
        "python", "-m", "backtest.optimize_ensemble",
        "--symbol", symbol,
        "--trials", str(default_trials),
        "--initial-cash", str(default_initial_cash)
    ]
    try:
        logger.info(f"⚙️ Running optimization for {symbol}...")
        subprocess.run(cmd, check=True)
        logger.info(f"✅ Completed: {symbol}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Optimization failed for {symbol}: {e}")

# === Main Loop ===
for symbol in symbols:
    run_ensemble_optimization(symbol)

logger.info("🏁 Daily auto-tuning completed.")
