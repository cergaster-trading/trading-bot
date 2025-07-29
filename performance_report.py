# performance_report.py
import pandas as pd
import numpy as np

# 1) Load your trade log
df = pd.read_csv("trade_log.csv", parse_dates=["timestamp"])
if df.empty:
    print("No trades logged yet.")
    exit()

# 2) Pair up buys & sells to compute per‐trade P&L
trades = []
for sym in df.symbol.unique():
    sym_df = df[df.symbol == sym].sort_values("timestamp")
    buys = sym_df[sym_df.side=="buy"].reset_index()
    sells = sym_df[sym_df.side=="sell"].reset_index()
    for i in range(min(len(buys), len(sells))):
        b = buys.loc[i]
        s = sells.loc[i]
        pnl = (s.price - b.price) * b.qty
        trades.append({
            "symbol": sym,
            "entry": b.timestamp, "exit": s.timestamp,
            "qty": b.qty,
            "pnl": pnl
        })
trades_df = pd.DataFrame(trades)
if trades_df.empty:
    print("No complete round‐trip trades yet.")
    exit()

# 3) Win rate
total_trades = len(trades_df)
wins = (trades_df.pnl > 0).sum()
win_rate = wins / total_trades * 100

# 4) Equity curve & Max Drawdown
#    cumulative P&L over time, then rolling peak‐to‐trough
equity = trades_df.sort_values("exit").pnl.cumsum()
running_max = equity.cummax()
drawdowns = (equity - running_max) / running_max
max_drawdown = drawdowns.min() * 100  # as percent

# 5) Print summary
print(f"Total trades: {total_trades}")
print(f"Wins:          {wins}")
print(f"Win rate:      {win_rate:.1f}%")
print(f"Max drawdown:  {max_drawdown:.1f}%")
