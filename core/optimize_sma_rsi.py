import json
import logging
import optuna

from core.config import SYMBOLS
from indicators.sma_rsi import calculate_sma_rsi
from tools.data import get_price_data
from monitoring.telegram_utils import send_telegram_message as send_telegram

logger = logging.getLogger("optimize_sma_rsi")


# ─── Trading Simulation Logic ──────────────────────────────────────────────────
def simulate_trades(df, rsi_buy, rsi_sell):
    capital = 100000
    position = 0

    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        sma = df['SMA'].iloc[i]
        rsi = df['RSI'].iloc[i]

        if price > sma and rsi < rsi_buy and capital > 0:
            position = capital / price
            capital = 0
        elif price < sma and rsi > rsi_sell and position > 0:
            capital = position * price
            position = 0

    if position > 0:
        capital = position * df['close'].iloc[-1]

    return capital - 100000


# ─── Optuna Objective Function ─────────────────────────────────────────────────
def objective(trial, df):
    sma_period = trial.suggest_int("sma_period", 10, 40)
    rsi_period = trial.suggest_int("rsi_period", 10, 40)
    rsi_buy = trial.suggest_int("rsi_buy", 20, 40)
    rsi_sell = trial.suggest_int("rsi_sell", 60, 80)

    df = calculate_sma_rsi(df.copy(), sma_period, rsi_period)
    return simulate_trades(df, rsi_buy, rsi_sell)


# ─── Optimize One Symbol ───────────────────────────────────────────────────────
def optimize_sma_rsi_for_symbol(symbol):
    df = get_price_data(symbol)
    if df is None or df.empty:
        logger.warning(f"⚠️ No data for {symbol}")
        return None

    try:
        study = optuna.create_study(direction="maximize")
        study.optimize(lambda trial: objective(trial, df), n_trials=50)
        best_params = study.best_params
        best_value = study.best_value

        logger.info(f"✅ {symbol} SMA/RSI: {best_params} (${best_value:.2f})")
        send_telegram(f"📊 SMA/RSI optimized for {symbol}: {best_params} → +${best_value:.2f}")
        return best_params

    except Exception as e:
        logger.exception(f"❌ Optimization failed for {symbol}: {e}")
        send_telegram(f"❌ Optimization failed for {symbol}: {e}")
        return None


# ─── Entrypoint for Scheduled or Manual Run ────────────────────────────────────
def run_sma_rsi_optimizer():
    logger.info("📈 Starting SMA/RSI optimization...")
    send_telegram("📈 Starting SMA/RSI optimizer...")

    result = {}
    for symbol in SYMBOLS:
        best = optimize_sma_rsi_for_symbol(symbol)
        if best:
            result[symbol] = best

    try:
        with open("sma_rsi_tuned_params.json", "w") as f:
            json.dump(result, f, indent=2)
        logger.info("✅ SMA/RSI optimization complete and saved.")
        send_telegram("✅ SMA/RSI optimization complete and saved to `sma_rsi_tuned_params.json`")
    except Exception as e:
        logger.error(f"❌ Error saving SMA/RSI weights: {e}")
        send_telegram(f"❌ Error saving SMA/RSI weights: {e}")


# ─── For Manual Execution ──────────────────────────────────────────────────────
if __name__ == "__main__":
    run_sma_rsi_optimizer()
