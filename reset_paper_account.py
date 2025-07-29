import requests
from core import config

def reset_paper_account():
    API_KEY = config.API_KEY
    API_SECRET = config.API_SECRET
    BASE_URL = config.BASE_URL

    if "paper" not in BASE_URL:
        print("⚠️ This reset script only works for paper trading accounts.")
        return

    response = requests.post(
        f"{BASE_URL}/v2/account/reset",
        headers={
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": API_SECRET
        }
    )

    if response.status_code == 204:
        print("✅ Alpaca paper account successfully reset.")
    else:
        print(f"❌ Reset failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    reset_paper_account()
