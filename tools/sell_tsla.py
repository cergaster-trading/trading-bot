import config, urllib.request, urllib.parse, json

# Build Alpaca headers
H = {
    "APCA-API-KEY-ID":     config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
}

# 1) Fetch your TSLA position
req = urllib.request.Request(
    config.BASE_URL + "/v2/positions/TSLA",
    headers=H
)
pos = json.load(urllib.request.urlopen(req))
qty = int(float(pos["qty"]))
print(f"Current TSLA qty: {qty}")

if qty == 0:
    print("No TSLA to sell.")
    exit()

# 2) Place a market sell for all TSLA shares
payload = {
    "symbol": "TSLA",
    "qty":    qty,
    "side":   "sell",
    "type":   "market",
    "time_in_force": "day"
}
sell_req = urllib.request.Request(
    config.BASE_URL + "/v2/orders",
    data = json.dumps(payload).encode(),
    headers = {**H, "Content-Type":"application/json"},
    method = "POST"
)
sell_resp = json.load(urllib.request.urlopen(sell_req))
print("Sell order response:", sell_resp)
