import config, urllib.request, json

HEADERS = {
    "APCA-API-KEY-ID":     config.API_KEY,
    "APCA-API-SECRET-KEY": config.API_SECRET,
}

def list_open():
    url = config.BASE_URL + "/v2/orders?status=open"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        print("Open orders now:", r.read().decode())

if __name__ == "__main__":
    list_open()
