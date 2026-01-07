import time
import json
import os
import requests
import math

import threading
from weather_flask import run_flask

from weather_state import CITY_STATE, MIN_TEMP

# STFU Flask
import logging
logging.getLogger("werkzeug").setLevel(logging.WARNING)

VERBOSE = True

TIMEOUT = 4

LOG_FILE = os.getenv("LOG_FILE","")

# NEVER EVER EVER EVER LEAVE THE API KEYS IN PROD, I JUST DONT GIVE AN F with this key right now so...
# YOU MUST LEAVE THEM INSIDE AND .env file and not share ti but I DON'T GIVE A F right now... (I will 100% delete it later once the project is reviewed)
OPENWEATHER_URL = os.getenv("OPENWEATHER_URL","https://api.openweathermap.org/data/2.5/weather")
OPENWEATHER_API = os.getenv("OPENWEATHER_API","9de3ba080271dd0704768c93ce3e5077")

CENTRAL_GRAPHQL = os.getenv("CENTRAL_GRAPHQL", "")

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
    
    resp = requests.post(CENTRAL_GRAPHQL, json=payload, timeout=timeout, verify=False)
    resp.raise_for_status()
    data= resp.json()

    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data.get("data", {})

def request_cities_from_central() -> list[str]:
    query = """
    query findAllCitiesCp {
        findAllCitiesCp
    }
    """
    data = gql_post(query=query, timeout=5)
    cities_raw = data.get("findAllCitiesCp", []) or []
    
    # Ahora findAllCitiesCp devuelve directamente un array de strings
    cities = [c.strip() for c in cities_raw if c and c.strip()]
    return cities

def create_alert(city: str):
    mutation = """
    mutation createAlert($ciudad: String!) {
        createAlert(ciudad: $ciudad)
    }
    """

    variables = {"ciudad": city}

    try:
        gql_post(mutation, variables=variables, timeout=5)
        print_log(f"CENTRAL createAlert sent for city='{city}'")
    except Exception as e:
        print_log(f"Failed to createAlert for city '{city}': {e}")

def remove_alert(city: str):
    mutation = """
    mutation removeAlert($ciudad: String!) {
        removeAlert(ciudad: $ciudad)
    }
    """

    variables = {"ciudad": city}

    try:
        gql_post(mutation, variables=variables, timeout=5)
        print_log(f"CENTRAL removeAlert sent for city='{city}'")
    except Exception as e:
        print_log(f"Failed to removeAlert for city '{city}': {e}")

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
    for city, st in list(CITY_STATE.items()):
        try:
            temp = openweather_temp_for_city(city)
            st["last_temp"] = temp
            st["last_update"] = time.strftime("%H:%M:%S")
            print_log(f"OpenWeather city={city}, temp={temp}C")

            prev_alert = bool(st.get("alert", False))
            now_alert = temp < MIN_TEMP

            if now_alert and not prev_alert:
                st["alert"] = True
                create_alert(city=city)
                print_log(f"ALERT RAISED - city='{city}' temp={temp}C (threshold {MIN_TEMP}C)")
            elif (not now_alert) and prev_alert:
                st["alert"] = False
                remove_alert(city=city)
                print_log(f"ALERT REMOVED - city='{city}' temp={temp}C (threshold {MIN_TEMP}C)")
        
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
    
    threading.Thread(target=run_flask, daemon=True).start()
    print_log("Weather GUI started")

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