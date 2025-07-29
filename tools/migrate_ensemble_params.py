import json
import os

PARAMS_FILE = "ensemble_tuned_params.json"
TUNED_DIR = "backtest/tuned_params"
os.makedirs(TUNED_DIR, exist_ok=True)

with open(PARAMS_FILE, "r") as f:
    data = json.load(f)

new_data = {}

for symbol, value in data.items():
    # Case 1: already ensemble-style (strategy: weight)
    if all(isinstance(v, float) for v in value.values()):
        new_data[symbol] = value
        continue

    # Case 2: old-style with full param block
    strategy_name = value.get("strategy")
    if not strategy_name:
        print(f"⚠️ Skipping {symbol}: no strategy key found.")
        continue

    # Remove strategy key and write the rest as tuned params
    params = {k: v for k, v in value.items() if k != "strategy"}
    output_file = os.path.join(TUNED_DIR, f"{strategy_name}_{symbol}.json")
    with open(output_file, "w") as f_out:
        json.dump(params, f_out, indent=2)

    # Insert new ensemble-style format
    new_data[symbol] = {strategy_name: 1.0}
    print(f"✅ Converted {symbol} → {strategy_name} with weight 1.0")

# Save updated ensemble_tuned_params.json
with open(PARAMS_FILE, "w") as f:
    json.dump(new_data, f, indent=2)

print("\n🎉 Migration complete.")
