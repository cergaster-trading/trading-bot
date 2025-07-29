import config, urllib.request, urllib.parse, json

HEADERS = {
    "APCA-API-KEY-ID":     config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
}

def http_get(path, params=None):
    url = config.BASE_URL + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

# 1) Account overview
acct = http_get("/v2/account")
print("=== ACCOUNT INFO ===")
print(f"Cash:       {acct['cash']}")
print(f"Buying Pow: {acct['buying_power']}")
print(f"Equity:     {acct['equity']}")
print(f"Status:     {acct['status']}")

# 2) Positions
positions = http_get("/v2/positions")
print("\n=== POSITIONS ===")
for p in positions:
    print(f"{p['symbol']}: qty={p['qty']} @ market_value={p['market_value']}")

# 3) Open orders
orders = http_get("/v2/orders", {"status":"open"})
print("\n=== OPEN ORDERS ===")
for o in orders:
    print(f"{o['symbol']} {o['side']} {o['qty']} – status={o['status']}")

