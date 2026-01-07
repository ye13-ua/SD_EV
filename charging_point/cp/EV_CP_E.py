##### EV_CP_Engine ##############################################################################################
# ENV definitions:                                                                                              #
# Default Kafka Broker -> kafka:9092 || "kafka" in "kafka:9092" being the docker container running kafka server #
# Default Engine port -> 7000        || ie. each monitor connects to it's respective engine via "7000"          #
# Docker network env. -> ev_net                                                                                 #
# Execution prompt -> "python EV_CP_E.py"                                                                       #
#                                                                                                               #
# env. dependencies -> kafka                                                                                    #
#################################################################################################################

# Default libs
import socket
import time
import json
import os
import threading
import random
# TODO repalce print with log

# LOGGING SEGMENT
import logging

LOG_LEVEL = os.getenv("ENGINE_LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s | %(levelname)s | CP_ENGINE | %(message)s")

logger = logging.getLogger("CP_ENGINE")

# MAIN SEGMENT

# Traffic lights for multithread editing of the states
from threading import Lock
# Kafka
from kafka import KafkaProducer, KafkaConsumer

# Config
HOST = "0.0.0.0"
PORT = int(os.getenv("ENGINE_PORT","7000"))
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
CP_ID = None

# Estado de conexión a kafka, no tiene nada que ver con la habilidad de recibir/enviar mensajes, solo conexión
kafka_ok = True
CP_STATUS = "AUTH_PENDING"
CP_PRICE = None
CP_TARGET_CHARGE = 0.0
CP_CHARGE_PROCESS = 0.0
CP_PROCESS = None
CP_CHARGE_PRICE = None
CP_CAR_IS_CONNECTED = False
CP_DRIVER_ID = None
CP_DRIVER_ALIAS = None

CP_META_PATH = "cp_meta.json"

CP_CITY = None

_consumer_started = False
_consumer_lock = Lock()

PENDING_LOCAL_REQ = False
LOCAL_REQ = {
    "driver_id": CP_DRIVER_ID,
    "target_kwh": CP_TARGET_CHARGE
}

state_lock = Lock()

def load_cp_meta():
    global CP_CITY
    if os.path.exists(CP_META_PATH):
        try:
            with open(CP_META_PATH, "r") as f:
                meta = json.load(f)
            CP_CITY = meta.get("city", CP_CITY)
        except Exception as e:
            logger.warning(f"Failed to load cp meta: {e}")

def save_cp_meta():
    try:
        with open(CP_META_PATH, "w") as f:
            json.dump({"city": CP_CITY}, f)
    except Exception as e:
        logger.warning(f"Failed to save cp meta: {e}")

def _start_kafka_consumer_if_needed():
    global _consumer_started
    with _consumer_lock:
        if _consumer_started or not CP_ID:
            return
        t = threading.Thread(target=listen_central_commands, daemon=True)
        t.start()
        _consumer_started = True

# Respond to ping from monitor
def handle_monitor(conn):
    global kafka_ok, CP_ID, CP_STATUS, CP_PRICE, CP_DRIVER_ID, CP_CITY

    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())
        action = msg.get("action")

        if CP_STATUS == "BROKEN":
            print(f"[Engine] Ignoring monitor while BROKEN")
            return

        if action == "PING":
            response = {"status": CP_STATUS, "kafka_ok": kafka_ok, "car_connected": CP_CAR_IS_CONNECTED, "price_kwh": CP_PRICE, "city": CP_CITY}
            
            if CP_STATUS == "CHARGING_CENTRAL":
                response.update({
                "target_kwh": CP_TARGET_CHARGE,
                "current_cost": CP_CHARGE_PRICE,
                "charging_process": CP_CHARGE_PROCESS,
                "driver_id": CP_DRIVER_ID
            })
            
            if PENDING_LOCAL_REQ and CP_STATUS == "WAITING":
                response.update({
                    "local_request": {
                        "cp_id": CP_ID,
                        "driver_id": LOCAL_REQ["driver_id"],
                        "target_kwh": LOCAL_REQ["target_kwh"]
                    }
                })

            
            
            conn.sendall(json.dumps(response).encode())
            #if CP_ID:
            #    publish_status("ACTIVE")
        elif action == "AUTH":
            if "cp_id" in msg:
                if CP_ID is None:
                    CP_ID = str(msg["cp_id"])
                    CP_PRICE = msg["cp_price"]
                    CP_STATUS = "AUTH_SUCCESS"
                    print (f"[Engine] Linked to CP_ID {CP_ID}")
                    _start_kafka_consumer_if_needed()
                incoming_city = msg.get("city")
                if incoming_city:
                    with state_lock:
                        CP_CITY = incoming_city
                    save_cp_meta()
            response = {"status": CP_STATUS, "kafka_ok":kafka_ok}
            conn.sendall(json.dumps(response).encode())
            CP_STATUS = "ACTIVE"
        
        elif action == "SIMULATE_LOCAL":
            simulate_local_use()
            response = {"status": "WAITING", "local_request": LOCAL_REQ}
            conn.sendall(json.dumps(response).encode())
        
        elif action == "SIMULATE_ENGINE_DOWN":
            threading.Thread(target=simulate_engine_down, args=(12,), daemon=True).start()
            response = {"status": "BROKEN", "kafka_ok": kafka_ok}
            conn.sendall(json.dumps(response).encode())


    except Exception as e:
        print(f"[Engine] Error handling monitor: {e}")
    finally:
        conn.close()

# Listens for kafka topic commands
def listen_central_commands():
    global kafka_ok, CP_ID
    # Attempting to connect to cafca and retrieve topic relevant data
    try:
        # Consumer definition
        consumer = KafkaConsumer(
            "Central.CP.Commands",
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id=f"cp_engine_{CP_ID}"
        )
        kafka_ok = True
        print(f"[Engine] Listening for commands from CENTRAL via Kafka...")
        # For each message we retrieve we process it accordingly
        for message in consumer:
            # Retrieve the targer value
            cmd = message.value
            target = str(cmd.get("target", "")).upper()

            # If we are a/the target we react accordingly
            if target == "ALL":
                handle_central_command(cmd)
            elif target == "ONE":
                cp_id = cmd.get("cpId")
                if cp_id and str(cp_id) == str(CP_ID):
                    handle_central_command(cmd)
                else:
                    continue # we ignore the call
            else:
                print(f"[Engine] Invalid target field: {target}")
    except Exception as e:
        print(f"[Engine] Kafka-Central consumer error: {e}")

# Handles command recieved via kafka from the central
def handle_central_command(cmd):
    global PENDING_LOCAL_REQ, CP_STATUS, CP_DRIVER_ID, CP_CAR_IS_CONNECTED, CP_TARGET_CHARGE, CP_PRICE, CP_CITY
    
    if CP_STATUS == "BROKEN":
        print(f"[Engine] Ignoring command while BROKEN: {cmd.get('action')}")
        return
    if CP_STATUS == "FINISHED_CHARGING":
        print(f"[Engine] Ignoring command 4 second timeout rule: {cmd.get('action')}")
        return
    
    action = cmd.get("action", "").upper()
    if action == "STOP":
        with state_lock:
            if CP_STATUS == "CHARGING_CENTRAL":
                save_current_session()
            if CP_STATUS == "WAITING":
                PENDING_LOCAL_REQ = False
            CP_STATUS = "OUT_OF_SERVICE"
        return
    elif action == "START":
        CP_STATUS = "ACTIVE"
        recover_previous_session()
    elif action == "CHARGE":
        with state_lock:
            PENDING_LOCAL_REQ = False
            CP_CAR_IS_CONNECTED = True

            CP_DRIVER_ID = str(cmd.get("driverId")).upper()
            CP_TARGET_CHARGE = float(cmd.get("target_charge", 0))
        simulate_app_use()
        CP_CAR_IS_CONNECTED = False
        CP_DRIVER_ID = None
    elif action == "UPDATE_PRICE":
        CP_PRICE = cmd.get("newPrice")
    elif action == "UPDATE_CITY":
        new_city = cmd.get("newCity")
        if not new_city:
            logger.warning("UPDATE_CITY recieved without newCity")
            return
        with state_lock:
            CP_CITY = new_city
        save_cp_meta()
        logger.info(f"City updated via Central: {new_city}")
    elif action == "BROKEN":
        with state_lock:
            if CP_STATUS == "CHARGING_CENTRAL":
                save_current_session()
            if CP_STATUS == "WAITING":
                PENDING_LOCAL_REQ = False
        simulate_engine_down()
        return
    elif action == "DRIVER_DISCONNECT":
        simulate_driver_disconnect()
        return
    else:
        print(f"[Engine] Unknown command action: {action}")

# stub
# Simulates breakdown or other issue
def simulate_local_fault():
    global CP_STATUS
    CP_STATUS = "BROKEN"

def simulate_engine_down(t=12):
    global CP_STATUS
    print(f"[Engine] Simulating ENGINE DOWN for {t} seconds...")
    prev_status = CP_STATUS
    CP_STATUS = "BROKEN"
    time.sleep(t)
    CP_STATUS = prev_status if prev_status != "BROKEN" else "ACTIVE"
    print("[Engine] ENGINE recovered.")

def simulate_driver_disconnect():
    global CP_STATUS, CP_TARGET_CHARGE, CP_CAR_IS_CONNECTED, CP_DRIVER_ID, PENDING_LOCAL_REQ, LOCAL_REQ
    
    CP_STATUS = "ACTIVE"
    CP_CAR_IS_CONNECTED = False
    
    return

# stub
# Simulates using the CP's own interface to recharge the car
def simulate_local_use():
    global CP_STATUS, CP_TARGET_CHARGE, CP_CAR_IS_CONNECTED, CP_DRIVER_ID, PENDING_LOCAL_REQ, LOCAL_REQ
    if CP_STATUS == "CHARGING_CENTRAL":
        return
    with state_lock:
        CP_CAR_IS_CONNECTED = True
        CP_STATUS = "WAITING"
        CP_DRIVER_ID = random.randint(1,3)
        CP_TARGET_CHARGE = round(random.uniform(3, 12), 2)
        PENDING_LOCAL_REQ = True
        LOCAL_REQ = {
            "driver_id": CP_DRIVER_ID,
            "target_kwh": CP_TARGET_CHARGE
        }


# Simulate charging petition from Centreal
def simulate_app_use():
    global CP_STATUS, CP_TARGET_CHARGE, CP_CHARGE_PRICE, CP_DRIVER_ALIAS, CP_CAR_IS_CONNECTED, CP_CHARGE_PROCESS, CP_STATUS
    if not CP_CAR_IS_CONNECTED:
        print(f"[Engine] Car not connected, petition refused")

    CP_STATUS = "CHARGING_CENTRAL"
    CP_CHARGE_PRICE = 0
    CP_CHARGE_PROCESS = 0
    while CP_CHARGE_PROCESS < CP_TARGET_CHARGE:
        if (CP_STATUS in ("OUT_OF_SERVICE", "BROKEN")):
            save_current_session()
            return
        if (CP_CHARGE_PROCESS+1) <= CP_TARGET_CHARGE:
            CP_CHARGE_PROCESS += 1
        else:
            CP_CHARGE_PROCESS += CP_TARGET_CHARGE-CP_CHARGE_PROCESS
        CP_CHARGE_PRICE += CP_PRICE
        time.sleep(1)
    CP_CHARGE_PROCESS = CP_TARGET_CHARGE
    CP_CHARGE_PRICE = 0
    CP_STATUS = "FINISHED_CHARGING"
    time.sleep(4)
    CP_STATUS = "ACTIVE"

def save_current_session():
    session = {
        "cp_id": CP_ID,
        "driver_id": CP_DRIVER_ID,
        "driver_alias": CP_DRIVER_ALIAS,
        "status": CP_STATUS,
        "charged_kwh": CP_CHARGE_PROCESS,
        "target_kwh": CP_TARGET_CHARGE,
        "price_kwh": CP_PRICE,
        "total_cost": round(CP_CHARGE_PRICE, 3) if CP_CHARGE_PRICE else 0,
        "city": CP_CITY,
        "timestamp": time.time()
    }

    try:
        with open(f"session_{CP_ID}.json", "w") as f:
            json.dump(session, f, indent=4)
        print(f"[ENGINE] Saved session: {CP_DRIVER_ID} ({CP_CHARGE_PROCESS:.2f} kWh, {CP_CHARGE_PRICE:.2f}€)")
    except Exception as e:
        print(f"[Engine] Error while saving session: {e}")

def recover_previous_session():
    global CP_DRIVER_ID, CP_DRIVER_ALIAS, CP_CHARGE_PROCESS, CP_TARGET_CHARGE, CP_CHARGE_PRICE, CP_PRICE
    path = f"session_{CP_ID}.json"
    if not os.path.exists(path):
        return False

    try:
        with open(path, "r") as f:
            session = json.load(f)
        os.remove(path)
        CP_DRIVER_ID = session.get("driver_id")
        CP_DRIVER_ALIAS = session.get("driver_alias")
        CP_TARGET_CHARGE = session.get("target_kwh", 0)
        CP_CHARGE_PROCESS = session.get("charged_kwh", 0)
        CP_CHARGE_PRICE = session.get("total_cost", 0)
        CP_PRICE = session.get("price_kwh", CP_PRICE)
        CP_CITY = session.get("city", CP_CITY)
        print(f"[Engine] Recovered previous session: {CP_CHARGE_PROCESS:.1f}/{CP_TARGET_CHARGE} kWh ({CP_CHARGE_PRICE:.2f}€)")
        return True
    except Exception as e:
        print(f"[Engine] Error recovering session: {e}")
        return False
            

# Defacto main function
def start_server():
    # Initialize sockets
    load_cp_meta()
    recover_previous_session()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen()
    print(f"[{CP_ID}] Engine listening on port {PORT}")

    # Monitor will persistently check the status via pings after connecting via sockets
    while True:
        conn, _ = s.accept()
        # For each time we need to handle the monitor, we spawn a thread
        threading.Thread(target=handle_monitor, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()