import config, urllib.request, json

HEADERS = {
    "APCA-API-KEY-ID":     config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
}

def cancel_all():
    url = config.BASE_URL + "/v2/orders?status=open"
    req = urllib.request.Request(url, headers=HEADERS, method="DELETE")
    with urllib.request.urlopen(req) as r:
        payload = r.read().decode()
    print("Canceled orders response:", payload)

if __name__ == "__main__":
    cancel_all()
