import schedule
import time
import logging
import threading
from datetime import datetime
from subprocess import Popen
from trading_bot import run_bot
from monitoring.telegram_utils import send_telegram_message as send_telegram


def start_bot():
    logging.info("[Scheduler] Starting trading bot...")
    try:
        run_bot()
    except Exception as e:
        logging.exception("❌ Error running trading bot")
        send_telegram(f"❌ Scheduler error in trading bot: {e}")


def run_ensemble_optimizer():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[Scheduler] Running ensemble optimizer at {now}")
    try:
        Popen(["python", "backtest/optimize_ensemble.py"])
        send_telegram(f"⚙️ Running ensemble optimizer at {now}")
    except Exception as e:
        logging.exception("❌ Error running ensemble optimizer")
        send_telegram(f"❌ Scheduler error in ensemble optimizer: {e}")


def run_sma_rsi_optimizer():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[Scheduler] Running SMA/RSI optimizer at {now}")
    try:
        Popen(["python", "backtest/optimize_sma_rsi.py"])
        send_telegram(f"📈 Running SMA/RSI optimizer at {now}")
    except Exception as e:
        logging.exception("❌ Error running SMA/RSI optimizer")
        send_telegram(f"❌ Scheduler error in SMA/RSI optimizer: {e}")


def schedule_tasks():
    # ─── Run bot once at startup ─────────────────────────────
    threading.Thread(target=start_bot, daemon=True).start()

    # ─── Schedule Optimizers ────────────────────────────────
    schedule.every().day.at("20:30").do(run_ensemble_optimizer)
    schedule.every().sunday.at("19:30").do(run_sma_rsi_optimizer)

    logging.info("[Scheduler] All tasks scheduled ✅")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    schedule_tasks()
