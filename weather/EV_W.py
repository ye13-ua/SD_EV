import time
import json
import os
import requests
import math

VERBOSE = True

TIMEOUT = 4
MIN_TEMP = 0

LOG_FILE = os.getenv("LOG_FILE","")

OPENWEATHER_URL = os.getenv("OPENWEATHER_URL","")
OPENWEATHER_API = os.getenv("OPENWEATHER_API","")

CENTRAL_GRAPHQL = os.getenv("CENTRAL_GRAPHQL", "")

CITY_STATE = {}

def print_log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[EV_W] {ts} :: {msg}"
    print(line)
    save_to_logs(line)

def save_to_logs(msg):
    try:
        entry = {"timestamp": time.time(), "message": msg}
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

# Request only the list of the cities
def gql_post(
        query: str,
        variables: dict | None = None,
        timeout: int = 5
) -> dict:
    if not CENTRAL_GRAPHQL:
        raise RuntimeError("CENTRAL_GRAPHQL is empty (set env var).")
    
    payload = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    
    resp = requests.post(CENTRAL_GRAPHQL, json=payload, timeout=timeout)
    resp.raise_for_status()
    data= resp.json()

    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data.get("data", {})

def request_cities_from_central() -> list[str]:
    query = """
    query findAllCiudades {
        findAllCiudades {
            ciudad
        }
    }
    """
    data = gql_post(query=query, timeout=5)
    rows = data.get("findAllCiudades", []) or []

    cities = []
    seen = set()
    for row in rows:
        c = (row.get("ciudad") or "").strip()
        if not c:
            continue
        key = c.lower()
        if key not in seen:
            seen.add(key)
            cities.append(c)
    return cities

def notify_central_city(city: str, status: str, temperature: float):
    mutation = """
    mutation NotifyWeather($input: WeatherAlertInput!) {
        notifyWeather(input: $input) {
            ok
            message
        }
    }
    """
    
    # Send only the city and it's status
    variables = {
        "input": {
            "ciudad": city,
            "status": status,
            "temperature": temperature
        }
    }

    try:
        data = gql_post(mutation, variables=variables, timeout=5)
        result = data.get("notifyWeather", {})
        print_log(f"CENTRAL notified city='{city}' status={status} temp={temperature} -> {result}")

    except Exception as e:
        print_log(f"Failed to notify CENTRAL for city {city}: {e}")

def openweather_temp_for_city(city: str) -> float:
    if not OPENWEATHER_URL or not OPENWEATHER_API:
        raise RuntimeError("OPENWEATHER_URL or OPENWEATHER_API missing (set env vars).")
    params = {
        "q": city,
        "appid": OPENWEATHER_API,
        "units": "metric"
    }
    resp = requests.get(OPENWEATHER_URL, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()

    main = data.get("main") or {}
    if "temp" not in main:
        raise RuntimeError(f"OpenWeather response missing main.temp for city='{city}': {data}")
    return float(main["temp"])

def sync_city_state(cities: list[str]):
    for city in cities:
        if city not in CITY_STATE:
            CITY_STATE[city] = {
                "alert": False,
                "last_temp": None
            }
            print_log(f"Registered new city: '{city}'")

def weather_cycle():
    for city, st in list (CITY_STATE.items()):
        try:
            temp = openweather_temp_for_city(city)
            st["last_temp"] = temp
            print_log(f"OpenWeather city={city}, temp={temp}C")

            prev_alert = bool(st.get("alert"), False)
            now_alert = temp < MIN_TEMP

            if now_alert and not prev_alert:
                st["alert"] = True
                notify_central_city(city, "ALERT", temp)
                print_log(f"ALERT ENTER city='{city}' temp={temp}C (threshold {MIN_TEMP}C)")
            elif (not now_alert) and prev_alert:
                st["alert"] = False
                notify_central_city(city, "RESTORE", temp)
                print_log(f"ALERT EXIT city='{city}' temp={temp}C (threshold {MIN_TEMP}C)")
        
        except Exception as e:
            print_log(f"ERROR weather cycle city='{city}': {e}")

# MAIN SEGMENT
def main():
    if not CENTRAL_GRAPHQL:
        print_log("FATAL: CENTRAL_GRAPHQL not set.")
        return

    if not OPENWEATHER_URL or not OPENWEATHER_API:
        print_log("FATAL: OPENWEATHER_URL/OPENWEATHER_API not set.")
        return
    
    cycle = 0
    while True:
        cycle += 1

        if cycle == 1 or (cycle % 3 == 0):
            try:
                cities = request_cities_from_central()
                print_log(f"Fetched {len(cities)} cities from CENTRAL: {cities}")
                sync_city_state(cities=cities)
            except Exception as e:
                print_log(f"ERROR requesting cities from CENTRAL: {e}")
        weather_cycle()
        time.sleep(TIMEOUT)

if __name__ == "__main__":
    main()