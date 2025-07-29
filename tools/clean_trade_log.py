import pandas as pd

# 1) Load both logs
trades = pd.read_csv('trade_log.csv',
                     names=['timestamp','symbol','side','qty','price'],
                     parse_dates=['timestamp'],
                     header=0)
fills  = pd.read_csv('fills_log.csv',
                     names=['fill_time','order_id','symbol','side','qty','price'],
                     parse_dates=['fill_time'],
                     header=0)

# 2) Normalize types
trades['qty']   = trades['qty'].astype(int)
trades['price'] = trades['price'].astype(float)
fills ['qty']   = fills ['qty'].astype(int)
fills ['price'] = fills ['price'].astype(float)

# 3) Merge: only keep trades that have a matching fill (by symbol, side, qty, price)
merged = pd.merge(
    trades,
    fills[['symbol','side','qty','price']],
    on=['symbol','side','qty','price'],
    how='inner'
).drop_duplicates()

# 4) Write back
merged.to_csv('trade_log_clean.csv', index=False,
              date_format='%Y-%m-%dT%H:%M:%SZ')

print(f"Cleaned {len(trades)} → {len(merged)} rows; wrote trade_log_clean.csv")
