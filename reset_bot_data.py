import os
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))

# Paths to reset
files_to_delete = [
    os.path.join(base_dir, "positions.json"),
    os.path.join(base_dir, "backtest", "backtest_results.csv"),
]

files_to_wipe = {
    os.path.join(base_dir, "fills_log.csv"): ["symbol", "side", "qty", "fill_price", "timestamp"],
    os.path.join(base_dir, "monitoring", "daily_summary.log"): None,
    os.path.join(base_dir, "monitoring", "performance_summary.csv"): ["date", "symbol", "realized", "unrealized", "total", "positions"]
}

for path in files_to_delete:
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Deleted {os.path.basename(path)}")

for path, headers in files_to_wipe.items():
    if os.path.exists(path):
        if headers:
            pd.DataFrame(columns=headers).to_csv(path, index=False)
            print(f"🔁 Wiped {os.path.basename(path)} to headers only")
        else:
            open(path, 'w').close()
            print(f"🧼 Cleared contents of {os.path.basename(path)}")
