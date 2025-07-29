# verify_positions.py
import config, urllib.request, urllib.parse, json

HEADERS = {
    "APCA-API-KEY-ID":     config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
}

req = urllib.request.Request(
    config.BASE_URL + "/v2/positions",
    headers=HEADERS
)
data = json.load(urllib.request.urlopen(req))

# Print each position symbol and qty
for p in data:
    print(f"{p['symbol']}: {p['qty']} shares")
