import urllib.request, json
from config import API_KEY, API_SECRET

# Endpoint for paper account
url = "https://paper-api.alpaca.markets/v2/account"
headers = {
    "APCA-API-KEY-ID":     API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
        print("✅ Auth OK!")
        print(f"Account: {data['account_number']}, Cash: ${data['cash']}")
except Exception as e:
    print("❌ Auth Failed:", e)
