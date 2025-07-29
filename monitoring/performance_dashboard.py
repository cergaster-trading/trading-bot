import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

FILL_LOG = "fills_log.csv"
DUMMY_ORDER_ID = "TEST-ORDER"

# --- Load fills log ---
try:
    fills = pd.read_csv(
        FILL_LOG,
        parse_dates=["fill_time"],
        index_col="fill_time"
    )
except FileNotFoundError:
    print(f"File '{FILL_LOG}' not found.")
    exit(1)

# --- Filter real orders only ---
fills = fills[fills["order_id"] != DUMMY_ORDER_ID]

if fills.empty:
    print("No real fills in log—nothing to plot.")
    exit(0)

# --- Compute P&L per fill ---
fills["pnl"] = (
    fills["filled_qty"]
    * fills["filled_price"]
    * fills["side"].str.lower().map({"sell": 1, "buy": -1})
)

# --- Daily & cumulative P&L ---
daily_pnl = fills["pnl"].resample("D").sum().fillna(0)
cum_pnl = daily_pnl.cumsum()

# --- Drawdown calculation ---
peak = cum_pnl.cummax()
drawdown = (cum_pnl - peak) / peak

# --- Sharpe ratio ---
sharpe = float("nan")
if daily_pnl.std() > 0:
    sharpe = daily_pnl.mean() / daily_pnl.std() * np.sqrt(252)

# --- Plot ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# 1. Cumulative P&L
ax1.plot(cum_pnl.index, cum_pnl.values, lw=2)
ax1.set_title(f"Cumulative P&L (Sharpe ≈ {sharpe:.2f})")
ax1.set_ylabel("USD")
ax1.grid(True)

# 2. Daily P&L
ax2.bar(daily_pnl.index, daily_pnl.values, width=0.8)
ax2.set_title("Daily P&L")
ax2.set_ylabel("USD / day")
ax2.grid(True)

# 3. Drawdown
ax3.fill_between(drawdown.index, drawdown.values * 100, 0, alpha=0.6)
ax3.set_title("Drawdown (%)")
ax3.set_ylabel("Drawdown %")
ax3.set_ylim(drawdown.min() * 110 if drawdown.min() < 0 else -0.01, 0)
ax3.grid(True)

# Final formatting
ax3.set_xlabel("Date")
fig.autofmt_xdate()
plt.tight_layout()
plt.show()
