from datetime import datetime
import pytz

def is_market_open():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    return now.weekday() < 5 and 9 <= now.hour < 16  # Mon–Fri, 9am–4pm ET
