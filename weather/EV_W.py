import time
import json
import os
import requests
import math
#TODO: make it so if a new CP is added, regions are updated automatically

#TODO: Use some easy acces front end (must be reactive, flask?)

#TODO: GRAPH QL

VERBOSE = True

TIMEOUT = 4
MIN_TEMP = 0
MAX_DISTANCE = 50

LOCAL_FILE = os.getenv("LOCAL_FILE","")
LOCALES = [] # example locale {CP_UUID, lat, long, last temp}
REGION_FILE = os.getenv("REGION_FILE","")
REGIONS = [] # General regions on which to call API {lat, long}
             # Let the minimum distance for a new instanec to be 50km, thus any new CP which is 50Km or more away from another, creates a new node

LOG_FILE = os.getenv("LOG_FILE","")

OPENWEATHER_URL = os.getenv("OPENWEATHER_URL","")
OPENWEATHER_API = os.getenv("OPENWEATHER_API","")

# Compute the distance between points
def haversine(lat1, lon1,lat2,lon2):
    R = 6371 # Km
    d_lat = math.radians(lat2-lat1)
    d_lon = math.radians(lon2-lon1)
    a = (math.sin(d_lat/2)**2 + 
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon/2)**2)
    return 2 * R * math.asin(math.sqrt(a))

def build_regions():
    global REGIONS

    if os.path.exists(REGION_FILE):
        with open(REGION_FILE, "r", encoding="utf-8") as f:
            REGIONS = json.load(f)
        print_log(f"Loaded {len(REGIONS)} regions from {REGION_FILE}")
        return
    print_log("Building regions from locales")

    for cp in LOCALES:
        lat = cp["lat"]
        lon = cp["lon"]

        assigned = False

        for region in REGIONS:
            d = haversine(lat,lon, region["lat"], region["lon"])
            if d < MAX_DISTANCE:
                # choose the closest one to it in the region
                assigned = True
                break
        if not assigned:
            REGIONS.append(
                {
                    "lat":lat,
                    "lon":lon,
                    "cps":[cp["cp_id"]],
                    "alert": False,
                    "last_temp": None
                }
            )
    with open(REGION_FILE, "w", encoding="utf-8") as f:
        json.dump(REGIONS, f, indent=4)
    print_log(f"Created {len(REGIONS)} regions.")

def load_locales():
    global LOCALES, LOCAL_FILE

    if not os.path.exists(LOCAL_FILE):
        print_log("Could not find LOCALES file. Requesting from CENTRAL...")
        request_locales()
        return

    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        LOCALES = json.load(f)
    
    if LOCALES:
        print_log(f"{len(LOCALES)} locales loaded. Sample: {LOCALES[0]}")
    else:
        print_log(f"Locales file was empty. Requesting from CENTTAL...")
        request_locales()

def request_locales():
    global LOCALES

    # use GRAPH QL
    # call Centrall and request locales
    # Add it to laceles
    # check if the coordinate is 50km or further from any ohter CP and create a new region, if not set it's region to the appropriate already created one

def notify_central(region, status: str, temp: float):
    payload = {
        "regionlat": region["lat"],
        "region_lon": region["lon"],
        "cp_id": region["cp_id"],
        "status": status,
        "temperature": temp
    }

    #  Send payload

def weather_call():
    # optimize the locales up to simple weather regions
    global REGIONS, MIN_TEMP

    for region in REGIONS:
        url = f"{OPENWEATHER_URL}?lat={region['lat']}&lon={region['lon']}&appid={OPENWEATHER_API}&units=metric"

        try:
            resp = requests.get(url)
            data = resp.json()
            temp = data["main"]["temp"]
            print_log(f"CALL, retrieved data for: {region}")
        except Exception as e:
            print_log(f"ERROR, could not retrieve data for {region}: {e}")

        prev_alert  = region["alert"]

        if temp < MIN_TEMP and not prev_alert:
            region["alert"] = True
            notify_central(region, "ALERT", temp)
            print_log(f"Region: {region} enter ALERT with T={temp}C")

        elif temp >= MIN_TEMP and prev_alert:
            region["alert"] = False
            notify_central(region, "RESTORE", temp)
        
        region["last_temp"] = temp
    

def print_log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[EV_W] {ts} :: {msg}")
    save_to_logs(msg)

def save_to_logs(msg):
    entry = {
        "timestamp": time.time(),
        "message": msg
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# MAIN SEGMENT
def main():
    load_locales()
    build_regions()

    while True:
        weather_call()
        time.sleep(TIMEOUT)

if __name__ == "__main__":
    main()