print("✅ Using Alpaca IEX fallback data.py")

import pandas as pd
from datetime import datetime, timedelta
import requests
from core import config  # ✅

def get_price_data(symbol, days=30):
    end = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    start = (datetime.utcnow() - timedelta(days=days)).replace(microsecond=0).isoformat() + "Z"

    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
    headers = {
        "APCA-API-KEY-ID": config.API_KEY,
        "APCA-API-SECRET-KEY": config.API_SECRET
    }
    params = {
        "start": start,
        "end": end,
        "timeframe": "1Day",
        "feed": "iex",
        "limit": 1000
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")

    raw_bars = response.json().get("bars", [])
    if not raw_bars:
        raise ValueError(f"No bars returned for {symbol}")

    df = pd.DataFrame(raw_bars)
    df["t"] = pd.to_datetime(df["t"])
    df.set_index("t", inplace=True)
    df.index.name = "datetime"

    df.rename(columns={
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "v": "volume"
    }, inplace=True)

    return df


