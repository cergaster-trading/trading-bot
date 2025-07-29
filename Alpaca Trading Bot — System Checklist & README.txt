# ✅ Alpaca Trading Bot — System Checklist & README

This README serves as a complete reference and operational checklist for your fully automated Alpaca trading bot setup.

---

## 📁 Folder Structure

```
alpaca_bot/
├── trading_bot.py               # Main bot loop (daily execution)
├── core/
│   ├── config.py               # Alpaca keys, symbol list, slippage
│   ├── broker.py               # Trade execution + stop-loss logic
│   └── ...
├── indicators/                 # Ensemble + SMA/RSI logic
├── tools/
│   ├── log_utils.py           # Logs stop-losses to CSV
│   └── ...
├── monitoring/
│   ├── daily_summary.py       # Sends P/L + position snapshot (5:30 PM)
│   ├── prometheus_metrics.py  # Exposes Prometheus metrics
│   └── telegram_utils.py      # Telegram alerts
├── stop_loss_log.csv          # Log of stop-loss orders placed
├── stop_fills_log.csv         # Log of triggered stop-losses
├── ensemble_tuned_params.json # Per-symbol optimized parameters
├── .env                       # Email credentials + flags
└── requirements.txt           # Dependencies (optional)
```

---

## 🧠 Bot Features

| Feature                             | Status |
|------------------------------------|--------|
| Multi-strategy trading (ensemble + SMA/RSI) | ✅    |
| Alpaca live order execution        | ✅    |
| Dynamic stop-loss per position     | ✅    |
| Avoids duplicate SL orders         | ✅    |
| Replaces outdated SL orders        | ✅    |
| Telegram alerts for trade actions  | ✅    |
| CSV logging for SL orders + fills  | ✅    |
| Daily email + Telegram P/L summary | ✅    |
| Prometheus metrics for uptime, SL  | ✅    |

---

## ⏰ Scheduled Tasks (Windows Task Scheduler)

### 1. **Trade Execution**
- **Runs:** Every weekday at market open (e.g. 9:31 AM)
- **Script:** `python trading_bot.py`

### 2. **Stop-Loss Fill Monitoring**
- **Runs:** Every weekday at 5:00 PM
- **Script:** `monitor_stop_fills.py`
- **BAT file:** `check_stop_fills.bat`

### 3. **Daily P/L Summary**
- **Runs:** Every weekday at 5:30 PM
- **Script:** `monitoring/daily_summary.py`
- **BAT file:** `daily_summary.bat`

---

## 🔐 .env File Required Variables

```env
EMAIL_ENABLED=true
EMAIL_FROM=cergaster@gmail.com
EMAIL_TO=cergaster@gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=cergaster@gmail.com
EMAIL_PASSWORD=<your 16-digit Gmail App Password>
```

---

## 📈 Prometheus Metrics Tracked

| Metric                          | Description |
|--------------------------------|-------------|
| `bot_uptime_seconds`           | Bot runtime in seconds |
| `bot_trades_total`             | Total trades executed |
| `rebalance_attempts_total`     | Rebalance attempts |
| `rebalance_successes_total`    | Successful rebalances |
| `rebalance_failures_total`     | Failed rebalances |
| `stop_loss_orders_total{symbol}` | Stop-losses placed |

Optional future metrics:
- `stop_loss_fills_total{symbol}` (if added)

---

## 🛠 Logs

- `stop_loss_log.csv` — every SL order placed
- `stop_fills_log.csv` — when stop-losses are triggered (filled)

---

## 📬 Alerts

- Trade entries/exits: via Telegram
- Stop-loss placements: via Telegram
- Stop-loss fills: via Telegram + CSV
- Daily summary: via Telegram + Email

---

## 🧪 Test Commands

```bash
# Run the bot manually
python trading_bot.py

# Check SL fills
python monitor_stop_fills.py

# Run daily summary manually
python monitoring/daily_summary.py
```

---

## 🧯 Troubleshooting

| Issue                          | Fix |
|-------------------------------|------|
| `ModuleNotFoundError: core`   | Add project root to `sys.path` in script |
| Email not sending             | Double check `.env`, use 16-digit Gmail App Password |
| Telegram not alerting         | Check `BOT_TOKEN` + `CHAT_ID` in Telegram setup |
| Prometheus not loading        | Ensure `start_prometheus_server()` is called once |

---

## 🚀 You Are Now Fully Automated

Your bot is:
- Autonomous
- Defended
- Transparent
- Monitored

Let it run. Observe. Learn. 

When you're ready to evolve — revisit this README and take the next step.

---

**Created with 🤖 by ChatGPT**
