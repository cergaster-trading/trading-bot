# run_forever.py

import subprocess
import time
import os
import logging
from datetime import datetime

# === Logging Setup ===
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_FILE = "logs/run_forever.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Constants ===
RESTART_DELAY = 60  # seconds
BOT_FILENAME = "trading_bot.py"
PYTHON_EXECUTABLE = r"venv310\Scripts\python.exe"  # Use full path to venv Python

def start_trading_bot():
    while True:
        logger.info("Auto-restart wrapper for trading_bot.py is active.")
        logger.info("Launching trading_bot.py...")

        try:
            result = subprocess.run([PYTHON_EXECUTABLE, BOT_FILENAME])
            exit_code = result.returncode
        except Exception as e:
            logger.exception(f"Failed to start bot: {e}")
            exit_code = -1

        crash_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.warning(f"Bot exited unexpectedly at {crash_time} with code {exit_code}")
        logger.info(f"Restarting trading bot in {RESTART_DELAY} seconds...")
        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    start_trading_bot()
