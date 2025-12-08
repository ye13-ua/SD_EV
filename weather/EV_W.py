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

GRID_LAT_STEP = 0.5
GRID_LON_STEP = 0.5

LOCAL_FILE = os.getenv("LOCAL_FILE","")
LOCALES = [] # example locale {CP_UUID, lat, long, last temp}
REGION_FILE = os.getenv("REGION_FILE","")
REGIONS = [] # General regions on which to call API {lat, long}
             # Let the minimum distance for a new instanec to be 50km, thus any new CP which is 50Km or more away from another, creates a new node

LOG_FILE = os.getenv("LOG_FILE","")

OPENWEATHER_URL = os.getenv("OPENWEATHER_URL","")
OPENWEATHER_API = os.getenv("OPENWEATHER_API","")

GEOCODE_URL = os.getenv("GEOCODE_URL", "http://api.openweathermap.org/geo/1.0/direct")
CITY_CACHE = {}

CENTRAL_GRAPHQL = os.getenv("CENTRAL_GRAPHQL", "")

def geocode_city(city_name):
    if city_name in CITY_CACHE:
        return CITY_CACHE[city_name]

    if not OPENWEATHER_API:
        print_log("[WARNING] OPENWEATHER_API key not set; cannot geocode.")
        return None, None
    
    try:
        params = {
            "q": city_name,
            "limit": 1,
            "appid": OPENWEATHER_API
        }
        resp = requests.get(GEOCODE_URL, params=params, timeout=5)
        data = resp.json()

        if not data:
            print_log(f"[WARNING] No geocoding result for '{city_name}'")

        lat = data[0]["lat"]
        lon = data[0]["lon"]
        CITY_CACHE[city_name] = (lat, lon)
        print_log(f"Geocoded '{city_name}' at: ({lat}, {lon})")
        return lat, lon
    except Exception as e:
        print_log(f"[Error] Failed geocoding '{city_name}': {e}")
        return None, None

# New grid functionality
# Sets a CP to a closest fixed pint at the grid
# lat/lon being the points and step the grid step
# returns direct point from the grid
def snap_to_grid(lat, lon, step=0.5):
    grid_lat = round(lat / step) * step
    grid_lon = round(lon / step) * step
    return grid_lat, grid_lon

# Generate the grid with each of the points based on the available CPs. The regions don't even need to be connected and still should connect well enough
def assign_regions():
    global REGIONS

    region_map = {}

    for cp in LOCALES:
        lat, lon = cp["lat"], cp["lon"]
        glat, glon = snap_to_grid(lat, lon, 0.5)

        key = f"{glat},{glon}"
        if key not in region_map:
            region_map[key] = {
                "lat": glat,
                "lon": glon,
                "cps": [],
                "alert": False,
                "last_temp": None
            }

        region_map[key]["cps"].append(cp["cp_id"])

    REGIONS = list(region_map.values())

def request_locales():
    global LOCALES

    query = """
    query GetLocales {
        locales {
            cp_id
            city
        }
    }
    """

    try:
        resp = requests.post(
            CENTRAL_GRAPHQL,
            json={"query": query},
            timeout=5
        )
        data = resp.json()

        if "errors" in data:
            print_log(f"GraphQL error: {data['errors']}")
            return
        
        central_list = data["data"]["locales"]
        print_log(f"Fetched {len(central_list)} locales from CENTRAL via GraphQL.")

    except Exception as e:
        print_log(f"Failed to request locales from CENTRAL: {e}")

    known_ids = {cp["cp_id"] for cp in LOCALES}

    new_cps = [cp for cp in central_list if cp["cp_id"] not in known_ids]

    if new_cps:
        print_log(f"Detected {len(new_cps)} NEW CPs.")
    else:
        print_log("No new CPs found in a call.")

    for cp in new_cps:
        city = cp["city"]
        lat, lon = geocode_city(city)

        if lat is None or lon is None:
            print_log(f"[WARNING] Skipping new CP {cp['cp_id']} (city '{city}' cannot be geocoded)")
            continue

        LOCALES.append({
            "cp_id": cp["cp_id"],
            "city": city,
            "lat": lat,
            "lon": lon,
            "last_temp": None,
            "alert": False
        })

        print_log(f"Added new CP {cp['cp_id']} ({city}) at ({lat}, {lon})")

    if new_cps:
        assign_regions()
        print_log("Regions updated with new CPs.")

    print_log(f"{len(LOCALES)} CPs currently monitord in {len(REGIONS)} regions")

def notify_central(region, status: str, temp: float):
    mutation = """
    mutation NotifyWeather($input: WeatherAlertInput!) {
        notifyWeather(input: $input) {
            ok
            message
        }
    }
    """
    
    variables = {
        "input": {
            "cps": region["cps"],
            "status": status,
            "temperature": temp
        }
    }

    try:
        resp = requests.post(
            CENTRAL_GRAPHQL,
            json={"query":mutation, "variables":variables},
            timeout=5
        )
        data = resp.json()

        if "errors" in data:
            print_log(f"GraphQL error notifying CENTRAL: {data['errors']}")
            return

        result = data["data"]["notifyWeather"]
        print_log(f"CENTRAL notified ({status}) - {result}")

    except Exception as e:
        print_log(f"Failed to notify CENTRAL: {e}")

    #  Send payload via GRAPH QL (maybe)

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
    request_locales()
    i = 0
    while True:
        i += 1
        weather_call()
        if (i == 3):
            request_locales()
            i = 0
        time.sleep(TIMEOUT)

if __name__ == "__main__":
    main()