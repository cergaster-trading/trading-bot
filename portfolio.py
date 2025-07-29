import config
import urllib.request
import json

# ────────────────────────────────────────────────────────────────────────────────
# API Config
# ────────────────────────────────────────────────────────────────────────────────
HEADERS = {
    "APCA-API-KEY-ID": config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
}
BASE_URL = config.BASE_URL

# ────────────────────────────────────────────────────────────────────────────────
# HTTP Fallbacks for When Alpaca SDK is Unavailable
# ────────────────────────────────────────────────────────────────────────────────
def http_get(path):
    url = BASE_URL + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def http_post(path, data):
    url = BASE_URL + path
    body = json.dumps(data).encode("utf-8")
    headers = {**HEADERS, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)

# ────────────────────────────────────────────────────────────────────────────────
# Portfolio Fetching (via Alpaca SDK or HTTP Fallback)
# ────────────────────────────────────────────────────────────────────────────────
def get_portfolio_status(api=None):
    try:
        if api:
            account = api.get_account()._raw
            positions = [p._raw for p in api.list_positions()]
        else:
            account = http_get("/v2/account")
            positions = http_get("/v2/positions")

        return {
            "equity": float(account.get("equity", 0)),
            "cash": float(account.get("cash", 0)),
            "positions": [
                {
                    "symbol": p["symbol"],
                    "qty": float(p["qty"]),
                    "market_value": float(p["market_value"]),
                }
                for p in positions
            ]
        }

    except Exception as e:
        print(f"❌ Failed to fetch portfolio status: {e}")
        return {"equity": 0, "cash": 0, "positions": []}

# ────────────────────────────────────────────────────────────────────────────────
# Submit Order (via Alpaca SDK or HTTP Fallback)
# ────────────────────────────────────────────────────────────────────────────────
def submit_order(symbol, qty, side, type="market", time_in_force="gtc", api=None):
    try:
        if api:
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
            )
        else:
            data = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": type,
                "time_in_force": time_in_force,
            }
            order = http_post("/v2/orders", data)

        print(f"✅ Order submitted: {side.upper()} {qty} shares of {symbol}")
        return order

    except Exception as e:
        print(f"❌ Failed to submit order for {symbol}: {e}")
        return None
