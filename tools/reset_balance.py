# reset_balance.py
import urllib.request
import json
import config

API_URL = "https://paper-api.alpaca.markets/v2/account"
HEADERS = {
    "APCA-API-KEY-ID":     config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
    "Content-Type":        "application/json",
}

def main():
    new_cash = 17400
    data = json.dumps({"cash": new_cash}).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=data,
        headers=HEADERS,
        method="PATCH"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            print("Account reset response:")
            print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as e:
        print("Reset failed:", e, e.read().decode())

if __name__ == "__main__":
    main()
